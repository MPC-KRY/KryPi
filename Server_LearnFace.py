import cv2, os
import numpy as np
from PIL import Image




"""
Description: Function that takes received photos and converts them into readable format for opencv library.
Parameters: array : images -> reads images from specified folder.

"""
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    # Looping through all the image paths and loading the Ids and the images
    for imagePath in imagePaths:
        # Loading the image and converting it to gray scale and converting it into numpy array.
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        # getting the Id from the image
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids

"""
Description: Function that deletes newly saved photos. 
Parameters: str : name -> name of the users photos to be deleted.
            str : path -> path where those photos are saved.
"""
def deletePhotos(name,path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    for file in imagePaths:
        if os.path.isfile(file) and name in file:
            os.remove(file)


"""
Description: function that receives users face images converted into correct format, and the using LBPHFFace recognizer it learns to recognize users face.
"""
def TrainImages(id,name):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces , Id= getImagesAndLabels("faces")
    recognizer.train(faces, np.array(Id))
    #store data in file 
    recognizer.save(f"TrainData\{name}_{id}.yml")
    print(f"Image Trained and data stored in TrainData\{name}_{id}.yml ")
    deletePhotos(name,"faces")