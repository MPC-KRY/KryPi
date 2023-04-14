import cv2
import os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd

name, Id = '', ''
dic = {
    'Name': name,
    'Ids': Id
}

def store_data():
    global name, Id, dic
    name = str(input("Enter Name  "))
    Id = str(input("Enter Id   "))
    #os.makedirs(f'TrainingImage/{name}')
    dic = {
        'Ids': Id,
        'Name': name
    }
    c = dic
    return  c

def is_number(s):
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

def TakeImages():
    dict1 = store_data()
    
    if (name.isalpha() and is_number(Id)):
        if Id == '1':
            fieldnames = ['Name', 'Ids']
            with open('Profile.csv', 'w') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(dict1)
        else:
            fieldnames = ['Name', 'Ids']
            with open('Profile.csv', 'a+') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(dict1)
        
        cam = cv2.VideoCapture(1)
        detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        sampleNum = 0
        
        while (True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                sampleNum += 1
                cv2.imwrite(f"TrainingImage\\{name}\\" + name + "." + Id + '.' + str(sampleNum) + ".jpg", gray[y:y + h, x:x + w])
                
            cv2.imshow('Capturing Face for Login', img)
        
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            elif sampleNum > 140:
                break
            
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for Name: " + name + " with ID: " + Id
        print(res)
        print('Images save location is TrainingImage\\')
      
    else:
        if(name.isalpha()):
            print('Enter Proper Id')
        elif(is_number(Id)):
            print('Enter Proper name')
        else:
            print('Enter Proper Id and Name')
                    
        

TakeImages()
