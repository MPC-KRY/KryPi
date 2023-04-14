import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import time


def DetectFace(images,name2):

    ids = { 1: "Jakub" , 2 : "Vojta"}
    for key , val in ids.items():
        if val == name2:
            id = key
    print('Detecting Login Face')
    recognizer = cv2.face.LBPHFaceRecognizer_create()  #cv2.createLBPHFaceRecognizer()
    recognizer.read(f"TrainData\{name2}_{id}.yml")
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Process each image
    for idx, img in enumerate(images):
        #print(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        Face_Id = 'Not detected'

        # Drawing a rectagle around the face 
        #print(faces)
        for (x, y, w, h) in faces:
            Face_Id = 'Not detected'
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            Id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            print(Id, confidence)
            if (confidence < 40):
                if (Id == id):
                    name = name2

                Predicted_name = str(name)
                Face_Id = Predicted_name
                print(f"{name} {Id} {confidence} {Face_Id}")
            else:
                Predicted_name = 'Unknown'
                Face_Id = Predicted_name
                # Here unknown faces detected will be stored
                noOfFile = len(os.listdir("UnknownFaces")) + 1
                if int(noOfFile) < 100:
                    cv2.imwrite("UnknownFaces\Image" + str(noOfFile) + ".jpg", img[y:y + h, x:x + w])
                else:
                    pass
            cv2.putText(img, str(Predicted_name), (x, y + h), font, 1, (255, 255, 255), 2)
            
        cv2.imshow('Picture', img)
        cv2.waitKey(1)

        # Checking if the face matches for Login
        if Face_Id == 'Not detected':
            print("-----Face Not Detected, Try again------")
            pass
            
        elif Face_Id == name2 and Face_Id != 'Unknown' :
            print('----------Detected as {}----------'.format(Predicted_name))
            print('-----------login successfull-------')
            print('***********WELCOME {}**************'.format(Predicted_name))
            return True
        else:
            print('-----------Login failed please try agian-------')
            return False
