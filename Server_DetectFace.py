import cv2,os



"""
Description: Function that received images of users face and compares it to trained dataset. 
             If opencv library recognizes that user it return True value. Otherwise it return False as not recognized.
Parameters: array : images -> image data of persons face who want to login.
            str : name2 -> name of the user who wants to log in.
            int : Id -> Id of user who wants to log in.
Returns: boolean : True/False if it recognized user or not.
"""
def DetectFace(images,name2,Id):
    print('Detecting Login Face')
    recognizer = cv2.face.LBPHFaceRecognizer_create()  #cv2.createLBPHFaceRecognizer()
    recognizer.read(f"TrainData\{name2}_{Id}.yml")
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Process each image
    for idx, img in enumerate(images):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        Face_Id = 'Not detected'

        # Drawing a rectagle around the face 
        for (x, y, w, h) in faces:
            Face_Id = 'Not detected'
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

            """
            Core variable: distance_from_known_user -> value of that variable determines how much scanned persons face matches learned face of that user. 
                           The lower the number the similar the faces are and the more probalibity its correct user.
                           Range is not from 0 to 100, so we put it to 40, which should be enough to recognise user,
                           when we take into consideration the quality of webcam and the low number of pictures it had to train from.       
            """
            predicted_Id, distance_from_known_user = recognizer.predict(gray[y:y + h, x:x + w])
            print(predicted_Id, distance_from_known_user)
            if (distance_from_known_user < 40):
                if (predicted_Id == Id):
                    name = name2
                Predicted_name = str(name)
                Face_Id = Predicted_name
                print(f"User: {name} ID:{Id} Match(Lower = better): {distance_from_known_user}")
            else:
                Predicted_name = 'Unknown'
                Face_Id = Predicted_name
                # Here unknown faces detected will be stored
                noOfFile = len(os.listdir("UnknownFaces")) + 1
                if int(noOfFile) < 100:
                    cv2.imwrite("UnknownFaces\Image" + str(noOfFile) + ".jpg", img[y:y + h, x:x + w])
                else:
                    pass
        cv2.waitKey(1)

        # Checking if the face matches for Login
        if Face_Id == 'Not detected':
            print("-----Face Not Detected, Try again------")
            pass
            
        elif Face_Id == name2 and Face_Id != 'Unknown' :
            print('----------Detected as {}----------'.format(Predicted_name))
            return True
        else:
            print('-----------Login failed please try agian-------')
            return False
