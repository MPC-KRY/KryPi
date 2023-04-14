import binascii
import json
import socket
import NetworkUtils

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import load_der_public_key

import test_AES
import cv2
import os
import numpy as np
import pickle
import string
import Server_LearnFace
import csv
import Server_DetectFace
from Database import Database
from Database import User




class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
        self.ECDH_key = None

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"server is listening on {self.host}:{self.port}")
        self.conn, addr = self.sock.accept()

    def send_data(self, data):
        if self.conn is not None:
            NetworkUtils.send_row(self.conn, data)

    def send_data_AES(self, data):
        if self.conn is not None:
            data = test_AES.encrypt(data, self.ECDH_key, True)
            NetworkUtils.send_row(self.conn, data.encode())

    def receive_data(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            return data

    def receive_data_AES(self,tur):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            if len(data) != 0:
                try:
                    mes = test_AES.decrypt(data.decode(), self.ECDH_key)
                    return mes
                except:
                    return test_AES.decrypt(data.decode(), self.ECDH_key, False)


    def close(self):
        self.sock.close()

    def countDH(self):

        # accepts the client's public key and creates its own private key
        Alice_public_key_bytes = self.receive_data()
        Bob_private_key = ec.generate_private_key(ec.SECP384R1())

        # converts the ECDH public key to bytes and sends it to the client
        Bob_public_key_bytes = Bob_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.send_data(Bob_public_key_bytes)

        # calculates the secret key
        Alice_public_key = load_der_public_key(Alice_public_key_bytes)
        size = 32
        Bob_shared_key = Bob_private_key.exchange(ec.ECDH(), Alice_public_key)
        Bob_derived_key = HKDF(hashes.SHA256(), size, None, b'', ).derive(Bob_shared_key)

        self.ECDH_key = binascii.b2a_hex(Bob_derived_key)[:32]
        print("\nBob's derived key: ", binascii.b2a_hex(Bob_derived_key).decode())



def read_json_data(file_path):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_data

def receive_faceloginData():
    name = ""
    val = True
    while True:
        if val == True:
            message = server.receive_data_AES(True)
        else:
            message = server.receive_data_AES(False)
            if val == False and isinstance(message,str) and "<DEPARATOR>" in message:
                val = True
                return id,name
            pictures = pickle.loads(message)


        if val == False:
            for i,face in enumerate(pictures):
                if isinstance(face,str):
                    print(type(face))
                else:
                    cv2.imwrite(f"faces\{name}.{id}.{i+1}.jpg", face)
        if val == True and "<BEGIN>" in message :
            name = message.split("<BEGIN>")[-1]
            print(name)

            # user = User(username=name, hash="738478383904", salt="7388774783834", iteration=54, totp=356765,
            #     email="blahblah@boehhuhuhu.cz")
            # database.add_user(user)

            # if id == '1':
            #     fieldnames = ['Name','Ids']
            #     with open('Profile.csv','w') as f:
            #         writer = csv.DictWriter(f, fieldnames=fieldnames)
            #         writer.writeheader()
            #         writer.writerow(dict)
            # else:
            #     fieldnames = ['Name','Ids']
            #     with open('Profile.csv','a+') as f:
            #         writer = csv.DictWriter(f, fieldnames=fieldnames)
            #         writer.writerow(dict)

        if val == True and "<SEPARATOR>" in message:
            val = False


def Detect_Faces():
    server.send_data_AES("Hello")
    credential = server.receive_data_AES(True)
    data = server.receive_data_AES(False)
    #message3 = server.receive_data_AES(True)
    data = pickle.loads(data)
    bol = Server_DetectFace.DetectFace(data,credential)
    if bol == False:
        print(f"{bol} bol is ")
        server.send_data_AES("<AGAIN>")
        message = server.receive_data_AES
        if isinstance(message,str) and "<OK>" in message:
            Detect_Faces()

    if bol == True:
        server.send_data_AES("<AUTHORIZED>")
        print("Confirmed")
        return False
    else:
        return True
    




if __name__ == '__main__':
    database = Database("example")
    #user = database.get_user_by_name("Jakub")
    #user.data = "HbZErx23LSBWLkXJIPxGVq+dr4OmTx6p5MUO///cDXw4v+D/kpIl+gW1RhxBFpCXfICA1Vdv13QmoDy2UT/fVY0B0GzACy/gmf5GNTX1uQks9hRflnlSrWS7Qasw0gVY1njiognDHRNOcDEFss2I9kP6B3NAhFYN+oHc8P9R+z6g6i33/hiWAdXp8vOXmXRwpqxef3blNqDhf2AglLxUP0PFnYPoipXQvDuoS3lAcqOIiEd+s+5FmE6Eyq+6uADRzOV3Cp+WtqUbENkKNHCeKugNqXBhYXzPmO+JTq89K331djfjjhx5XFyn20D9/f+Coe9Ap4ZnCQk718B3q3tvclpqRekRmUHr8q+cesaZ5ILyztRVX+L3YykZAYQ1OI6sVt9i+4mHq5uzLYyzTnDycHHEWZu4PMEDe6dl9W0IWzfm/F6FV+iNUaRDvm50Z8EPfRPeE8XXkSrTc+M7cZVeUwUVHrSGSgWBPn3JrFh1kx/+y2SCOLd4egT29aQxA8uXhcrGk8WAl1Gb915eSDVGKKNJHgVziuBT6BA9df/AwQ8w7Ta+4iNBR6oAZWjDLpQtHw7jWx2AlbJ1CXhy5lmQuL7lz43/Zuesta3Gnoou8VMDAHDMuN8hcpFmNCCsNfQRkiBMt2jnibPqMHV1xdpIOda329ZvmtINKDATf+tEmna9g1gFKBt2LOUWncTjU0s67peIAKMC+PnoCnoKB73wm7cD29ePa5yri3515tVTRWHPC0iVRxLORNE2/tJICRcBCwf/sVFtu8S2iWLUfhgfBLVns40oX2R9aGjmhUpNXW/wgw5S1OS2UPMG6fJOsvEPKuZgs7SP+bFiLg9qSW4xM+Kll1/Wp6mdpaukJJISwiHOtV/R5MyM76CO1GFr+b7YqAeCvThc2eNym1cm0Sk87iwvkP6WCf+1+vhqXT+yMnnf6zoNr7x6zQjqAokv52OgZGmbBXkBOuWy9W21Dldn7jiaJQohjInKqU4Vd8UHVAXofTMdjmq0Iij5WWsjGhV/"
    #database.update_user(user)
    #print(db.get_users())
    # user = User(username='Jakub', hash="password", salt="123456", iteration=23, totp=20304,
    #             email="jakub@boe.cz")
    # database.add_user(user)
    # user = User(username='Matej', hash="123456", salt="123456", iteration=54, totp=356765,
    #             email="matej@boehhuhuhu.cz")
    # database.add_user(user)
    # users = database.get_users()
    # print(users)


    server = Server()
    server.listen()
    server.countDH()

    user = database.get_user_by_name("Jakub")
    data = user.data
    server.send_data_AES(data)

    while True:
        data = server.receive_data_AES(True)
        if data is not None:
            user = database.get_user_by_name("Jakub")
            user.data = data
            database.update_user(user)



    temp = True
    temp2 = True
    id, name = "",""
    vall = False
    #while True:
        #message = server.receive_data_AES(True)
        # if temp == True and isinstance(message,str) and "<STARTFACELOGIN>" in message:
        #     name = receive_faceloginData()
        #     #id = database.get_user_by_name(name).id
        #     print(id)

        # if isinstance(message,str) and "<ENDFACELOGIN>" in message and temp == True:
        #     Server_LearnFace.TrainImages(id,name)
        #     temp = False

        # if temp2 == True and isinstance(message,str) and "<STARTFACE>" in message:
        #     vall = Detect_Faces()
        # if isinstance(message,str) and "<ENDFACE>" in message:
        #     temp2 = False

        # if vall == False:
        #     print(8)
        #     with open('myfile.txt', 'r') as file:
        #         data = file.read()
        #         file.close()
        #     server.send_data_AES(data)
        #     vall = True

        # if temp == False and message is not None:
        #     pass
        #     # with open('myfile.txt', 'w') as file:
        #     #      file.write(message)
        #     #      file.close()
        #     #      server.close()