import os


dic = {1:"Jakub",2:"Vojta"}


face = "Jakub"
Id = 2
if face in dic:
    print(Id)

for i in dic:
    print(i)



def deletePhotos(name,path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    for i in imagePaths:
        print((os.path.split(i)[-1].split(".")[0]))

    #print(imagePaths)
    for file in imagePaths:
        if os.path.isfile(file) and name in file:
            os.remove(file)

deletePhotos("Honza","faces")
