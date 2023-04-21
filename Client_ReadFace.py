import cv2
import os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import pickle
import struct

class FaceCapturer:
    def __init__(self):
        self.name = ''

        self.dict = {}

    def store_data(self):
        self.name = str(input("Enter Name: "))

        
        self.dict = {
            'Name': self.name
        }
        
        return self.name

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
     
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
     
        return False

    def capture_images(self,username):
        #dict1 = self.store_data()
        if (username.isalpha()):
            
            cam = cv2.VideoCapture(0)
        
            
            detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

            sampleNum = 0
            images = []
            
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


if __name__ == '__main__':
    face_capturer = FaceCapturer()
    images = face_capturer.capture_images()
    data = pickle.dumps(images)

