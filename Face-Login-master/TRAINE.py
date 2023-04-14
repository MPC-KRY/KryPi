import cv2
import os

# set the path to the file where the trained data is stored
trained_data_file = "TrainData\Trainner.yml"

# set the confidence threshold for face recognition
confidence_threshold = 0.7

# create a face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# create a video capture object to capture frames from the camera
cap = cv2.VideoCapture(1)

# check if the trained data file exists
if os.path.exists(trained_data_file):
    # load the trained data
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read("TrainData\Trainner.yml")

while True:
    # capture a frame from the camera
    ret, frame = cap.read()

    # convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # detect the faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    # loop through the detected faces
    for (x, y, w, h) in faces:
        # crop the face image
        face_img = gray[y:y+h, x:x+w]

        # use the face recognition model to recognize the face
        if os.path.exists(trained_data_file):
            label, confidence = face_recognizer.predict(face_img)
            if label == 1 and confidence <= 25:
                print(f"THIS IS ME {label}, {confidence}")
                # draw a green rectangle around the face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                # add a label to the rectangle
                cv2.putText(frame, 'You', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            else:
                print(label, confidence)        
                # draw a red rectangle around the face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                # add a label to the rectangle
                cv2.putText(frame, 'Unknown', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            
            # draw a blue rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            # add a label to the rectangle
            cv2.putText(frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # display the frame
    cv2.imshow('Face Recognition', frame)

    # check if the user pressed the 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
