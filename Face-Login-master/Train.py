"""
@author: Santhosh R
"""
import cv2, os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd


def getImagesAndLabels(path):
    file_names = []

# Traverse the directory tree and visit all files
    for dirpath, dirnames, filenames in os.walk(os.path.join(path)):
        for filename in filenames:
            # Add the full path of the file to the list
            file_path = os.path.join(dirpath, filename)
            file_names.append(file_path)

    print(file_names)
    # Get the path of all the files in the folder
    # imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    # print(imagePaths)

    # Create empth face list
    faces = []
    # Create empty ID list
    Ids = []
    # Looping through all the image paths and loading the Ids and the images
    for imagePath in file_names:
        # Loading the image and converting it to gray scale
        pilImage = Image.open(imagePath).convert('L')
        # Now we are converting the PIL image into numpy array
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        
        Ids.append(Id)
    return faces, Ids

# Train image using LBPHFFace recognizer 
def TrainImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces , Id= getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    #store data in file 
    recognizer.save("TrainData\Trainner.yml")
    res = "Image Trained and data stored in TrainData\Trainner.yml "

    print(res)

   

TrainImages()
    