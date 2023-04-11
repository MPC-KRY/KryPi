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
    val = True
    while True:
        if val == True:
            message = server.receive_data_AES(True)
        else:
            message = server.receive_data_AES(False)
            if val == False and isinstance(message,str) and "<DEPARATOR>" in message:
                val = True
                return True
            pictures = pickle.loads(message)

        if val == False:
            for i,face in enumerate(pictures):
                if isinstance(face,str):
                    print(type(face))
                else:
                    cv2.imwrite(f"faces\{name}.{id}.{i+1}.jpg", face)
        if val == True and "<BEGIN>" in message :
            name = message.split("<SEP>")[0].split("<BEGIN>")[-1]
            id = message.split("<SEP>")[1]
            dict = {'Ids': id, 'Name': name}
            if id == '1':
                fieldnames = ['Name','Ids']
                with open('Profile.csv','w') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(dict)
            else:
                fieldnames = ['Name','Ids']
                with open('Profile.csv','a+') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(dict)

        if val == True and "<SEPARATOR>" in message:
            val = False


def Detect_Faces():
    print(1)
    server.send_data_AES("Hello")
    print(2)
    data = server.receive_data_AES(False)
    print(3)
    print("second")
    #message3 = server.receive_data_AES(True)
    data = pickle.loads(data)
    bol = Server_DetectFace.DetectFace(data)
    print(4)
    if bol == False:
        print(f"{bol} bol is ")
        server.send_data_AES("<AGAIN>")
        print(5)
        message = server.receive_data_AES
        print(6)
        if isinstance(message,str) and "<OK>" in message:
            print(7)
            Detect_Faces()

    if bol == True:
        server.send_data_AES("<AUTHORIZED>")
        print("Confirmed")
        return False
    else:
        return True
    




if __name__ == '__main__':
    server = Server()
    server.listen()
    server.countDH()




    temp = True
    temp2 = True
    while True:
        message = server.receive_data_AES(True)
        if temp == True and isinstance(message,str) and "<STARTFACELOGIN>" in message:
            receive_faceloginData()
        if isinstance(message,str) and "<ENDFACELOGIN>" in message and temp == True:
            Server_LearnFace.TrainImages()
            temp = False

        if temp2 == True and isinstance(message,str) and "<STARTFACE>" in message:
            vall = Detect_Faces()
        if isinstance(message,str) and "<ENDFACE>" in message:
            temp2 = False

        if vall == False:
            print(8)
            with open('myfile.txt', 'r') as file:
                data = file.read()
                file.close()
            server.send_data_AES(data)
            vall = True

        if temp == False and message is not None:
            pass
            # with open('myfile.txt', 'w') as file:
            #      file.write(message)
            #      file.close()
            #      server.close()