"""
@author: Santhosh R
"""
import cv2, os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd


def getImagesAndLabels(path,id):
    # Get the path of all the files in the folder
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    # Create empth face list
    faces = []
    # Create empty ID list
    Ids = []
    # Looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # Loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        #print(os.path.split(imagePath)[-1].split(".")[1])
        #Id = id
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        
        Ids.append(Id)
    return faces, Ids



def deletePhotos(name,path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    for file in imagePaths:
        if os.path.isfile(file) and name in file:
            os.remove(file)




# Train image using LBPHFFace recognizer 
def TrainImages(id,name):
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    faces , Id= getImagesAndLabels("faces",id)
    recognizer.train(faces, np.array(Id))
    #store data in file 
    recognizer.save(f"TrainData\{name}_{id}.yml")
    print(f"Image Trained and data stored in TrainData\{name}_{id}.yml ")
    deletePhotos(name,"faces")



   
    