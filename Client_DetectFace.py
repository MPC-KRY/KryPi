"""
@author: Santhosh R
"""
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import time
import pickle



# This will make sure no duplicates exixts in profile.csv(using Pandas here)
# Fuction to detect the face
def DetectFace():
    print('Detecting Login Face')
    sampleNum = 0

 
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Camera ON Everytime
    images = []
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
            if len(images) > 1:
                print("len 5")
                return pickle.dumps(images)

        cv2.imshow('Capturing Face for Login', frame)
                


        cv2.waitKey(1)
        




# while True:
#     try:
#         print(DetectFace())
#     except KeyboardInterrupt:
#         break
