import cv2,os


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
            predicted_Id, distance_from_known_user = recognizer.predict(gray[y:y + h, x:x + w])
            print(predicted_Id, distance_from_known_user)
            if (distance_from_known_user < 40):
                if (predicted_Id == Id):
                    name = name2
                Predicted_name = str(name)
                Face_Id = Predicted_name
                print(f"{name} {Id} {distance_from_known_user} {Face_Id}")
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
