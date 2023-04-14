import cv2
import os
import random 
import string


# for i in range(51):
#     if i < 10:
#         os.makedirs(f'TrainingImage/8000{i}')
#     else:
#         os.makedirs(f'TrainingImage/800{i}')




for i in range(51):

    name = ''.join(random.choices(string.ascii_letters, k=5))
    if i < 10:
        input_dir = f'TrainingImage/800{i}/'

    # Path to the output directory where cropped face regions will be saved
        output_dir = f'TrainingImage/8000{i}/'
    else:
        input_dir = f'TrainingImage/80{i}/'

    # Path to the output directory where cropped face regions will be saved
        output_dir = f'TrainingImage/800{i}/'
    # Load the face detector

    innn = 0
    for inn in os.listdir(output_dir):
        innn+=1
        new_filename = name + '.'+'800'+str(i) + '.'  +str(innn) + '.png'
        print(inn)
        print(new_filename)
        ja = os.path.join(output_dir, inn)
        da = os.path.join(output_dir, new_filename)
        os.rename(ja,da)








    # face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # for filename in os.listdir(input_dir):
    #     #print(filename)
    #     # Load the input image
    #     image = cv2.imread(os.path.join(input_dir, filename))

    #     # Convert the image to grayscale
    #     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #     # Detect faces in the grayscale image
    #     faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    #     # Loop over the detected faces
    #     for (x, y, w, h) in faces:
    #         # Extract the face region
    #         face = image[y:y+h, x:x+w]

    #         # Convert the face region to grayscale
    #         gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

    #         # Save the cropped and grayscale face region to a new file
    #         output_filename = os.path.join(output_dir, f'{filename}_face{x}_{y}.jpg')
    #         #print(output_filename)
    #         cv2.imwrite(output_filename, gray_face)

    # print('Done')