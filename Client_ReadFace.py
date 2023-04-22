import cv2
import pickle



# Class that scans users face, and sends that data to server.
class FaceCapturer:
    def __init__(self):
        self.name = ''
        self.dict = {}

    def capture_images(self,username):
        if (username.isalpha()):
            cam = cv2.VideoCapture(0)
            detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            sampleNum = 0
            images = []
            # While loop, where it scans for users face, and exits once it got 70 pictures of its face.
            while True:
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    face_frame = gray[y:y+h, x:x+w]

                    sampleNum += 1
                    images.append(face_frame)
                cv2.imshow('Capturing Face for Login', img)
                
                if cv2.waitKey(100) & 0xFF == ord('q') or sampleNum > 70:
                    break

            cam.release()
            cv2.destroyAllWindows()

            print(f'Captured {len(images)} images for Name: {username}')
            return pickle.dumps(images)

        else:
            if username.isalpha():
                print('Enter Proper ID')
            else:
                print('Enter Proper ID and Name')