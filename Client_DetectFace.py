import cv2
import pickle

# Function to detect the face

def DetectFace():
    print('Detecting Login Face')
    sampleNum = 0
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    images = []
    print("Taking pictures of your face, please look into the camera.")
    # infinite cycle, where it scan for users face.
    # when it scanned 3 pictures, it will exit and those pictures will be sent to server for detecting.
    while True:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)

        # Drawing a rectagle around the face 
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            face_frame = gray[y:y+h, x:x+w]
            sampleNum +=1
            images.append(frame)
        
        if len(images) > 3:
            print("Images of your face takes, please wait.")
            break

    cv2.imshow('Capturing Face for Login', frame)
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    return pickle.dumps(images)
