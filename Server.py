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
import pyotp
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# generate a new RSA key pair





class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
        self.ECDH_key = None
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.rsa_hash_sig_key = None

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



    def import_RSA(self):
        with open("private_key_RSA.pem", 'rb') as private_key_file:
            self.rsa_private_key = RSA.importKey(private_key_file.read())

        with open("public_key_RSA.pem", 'rb') as public_key_file:
            self.rsa_public_key = public_key_file.read()

        with open("hash.sig", 'rb') as hash_file:
            self.rsa_hash_sig_key = hash_file.read()


    def send_keys_RSA(self):
        self.send_data(self.rsa_public_key)
        self.send_data(self.rsa_hash_sig_key)



    def decrypt_RSA(self,data):
        return self.rsa_private_key.decrypt(data)



    def countDH(self, pub_key_client, priv_key_server):
        cipher_server = PKCS1_OAEP.new(priv_key_server)
        cipher_client = PKCS1_OAEP.new(pub_key_client)


        # accepts the client's public key and creates its own private key
        Alice_public_key_bytes = cipher_server.decrypt(self.receive_data())
        Bob_private_key = ec.generate_private_key(ec.SECP384R1())

        # converts the ECDH public key to bytes and sends it to the client
        Bob_public_key_bytes = Bob_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        temp = cipher_client.encrypt(Bob_public_key_bytes)
        self.send_data(temp)

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

    username = server.receive_data_AES(True)
    print(username)
    user = database.get_user_by_name(username)
    Id = user.id
    
    data = server.receive_data_AES(False)
    pictures = pickle.loads(data)

    for i,face in enumerate(pictures):
        if isinstance(face,str):
            pass
        else:
            print(face)
            cv2.imwrite(f"faces\{username}.{Id}.{i+1}.jpg", face)
    end = server.receive_data_AES(True)
    if isinstance(end,str) and "<ENDFACEREGISTER>" in end:
        Server_LearnFace.TrainImages(Id,username)
        return username

        # if val == True:
        #     message = server.receive_data_AES(True)
        #     user = database.get_user_by_name()
        # else:
        #     message = server.receive_data_AES(False)
        #     if val == False and isinstance(message,str) and "<DEPARATOR>" in message:
        #         val = True
        #         return name
        #     pictures = pickle.loads(message)


        # if val == False:
        #     for i,face in enumerate(pictures):
        #         if isinstance(face,str):
        #             print(type(face))
        #         else:
        #             cv2.imwrite(f"faces\{name}.{id}.{i+1}.jpg", face)
        # if val == True and "<BEGIN>" in message:
        #     name = message.split("<BEGIN>")[-1]
        #     print(name)
        # if val == True and "<SEPARATOR>" in message:
        #     val = False


def Detect_Faces():
    server.send_data_AES("Hello")
    username = server.receive_data_AES(True)
    user = database.get_user_by_name(username)
    Id = user.id
    faces = server.receive_data_AES(False)
    faces = pickle.loads(faces)
    bol = Server_DetectFace.DetectFace(faces,username,Id)
    if bol == False:
        server.send_data_AES("<AGAIN>")
        message = server.receive_data_AES
        if isinstance(message,str) and "<OK>" in message:
            Detect_Faces()
    if bol == True:
        server.send_data_AES("<AUTHORIZED>")
        print("Confirmed")
        return True, username
    else:
        return False, "notusername"
    


def DefaultLogin():
    username, password = server.receive_data_AES(True).split("<>")
    print(username, password)
    user = database.get_user_by_name(username)
    hash = user.hash

    if verify_password(username, password):
        print("ses tam Heslo")
        #koukne do DB jaky metody ma
        face,totp = True,True
        server.send_data_AES(f"{face}<>{totp}")
    else:  
        server.send_data_AES("Wrong password")
    
    choice = int(server.receive_data_AES(True))
    #FACE
    if choice == 1:
        #FACE part
        message = server.receive_data_AES(True)
        if isinstance(message,str) and "<FACEAUTH>" in message:
            authorized, username = Detect_Faces()

        pass
    #TOTP
    elif choice == 2:
        #TOTP part
        totp_code = server.receive_data_AES(True)
        totp_db = user.totp
        totp_now = pyotp.TOTP(totp_db).now()
        if int(totp_code) == int(totp_now):
            print("Je to spravne TOTP")
            authorized = True
    if authorized:
        server.send_data_AES("<AUTHORIZED>")
        return True, username
    else:
        return False, "notauthorized"


    



    #tvorba hesla
def passGen(username,password):
    salt = bytes([random.randint(0,255) for _ in range(16)])
    iteration = random.randint(10000,90000)
    user = database.get_user_by_name(username)
    password = password.encode()
    key_size = 128

    key = PBKDF2(password, salt, dkLen=key_size, count=iteration, hmac_hash_module=SHA256)
    user.hash = key
    user.salt = salt
    user.iteration = iteration
    database.update_user(user)
    #return key, salt, iteration
    

def verify_password(user, password):
    key_size = 128
    user = database.get_user_by_name(user)
    iteration = user.iteration
    salt = user.salt
    key = PBKDF2(password, salt, dkLen=key_size, count=iteration, hmac_hash_module=SHA256)
    return user.hash == key


def create_user():
    username, password, email = server.receive_data_AES(True).split("<>")
    user = database.get_user_by_name(username)
    if user is None:
        user = User(username=username, email=email)
        database.add_user(user)
        passGen(username,password)
        server.send_data_AES("User Created")
        create_TOTP(username)
    else:
        print("user exists")
        server.send_data_AES("User NOT Created")


def create_TOTP(username):
    alphabet = string.ascii_letters + string.digits
    totp_seed = ''.join(random.choice(alphabet) for i in range(16))
    user = database.get_user_by_name(username)
    user.totp = totp_seed
    database.update_user(user)
    print(totp_seed)





if __name__ == '__main__':

    server = Server()
    server.listen()
    server.import_RSA()
    server.send_keys_RSA()

    public_key_client_RSA = server.receive_data()
    cipher = PKCS1_OAEP.new(server.rsa_private_key)

    chunk_size = 256 # maximum length of ciphertext that can be decrypted is 256 bytes
    plaintext = b''
    for i in range(0, len(public_key_client_RSA), chunk_size):
        chunk = public_key_client_RSA[i:i+chunk_size]
        plaintext += cipher.decrypt(chunk)

    public_client_RSA = RSA.importKey(plaintext)

    server.countDH(public_client_RSA,server.rsa_private_key)
    database = Database("example")

    #register
    # username = input("username: ")
    # password = input("password: ")
    # user = User(username=username)
    # database.add_user(user)
    # passGen(username,password)

    # data = "HbZErx23LSBWLkXJIPxGVq+dr4OmTx6p5MUO///cDXw4v+D/kpIl+gW1RhxBFpCXfICA1Vdv13QmoDy2UT/fVY0B0GzACy/gmf5GNTX1uQks9hRflnlSrWS7Qasw0gVY1njiognDHRNOcDEFss2I9kP6B3NAhFYN+oHc8P9R+z6g6i33/hiWAdXp8vOXmXRwpqxef3blNqDhf2AglLxUP0PFnYPoipXQvDuoS3lAcqOIiEd+s+5FmE6Eyq+6uADRzOV3Cp+WtqUbENkKNHCeKugNqXBhYXzPmO+JTq89K331djfjjhx5XFyn20D9/f+Coe9Ap4ZnCQk718B3q3tvclpqRekRmUHr8q+cesaZ5ILyztRVX+L3YykZAYQ1OI6sVt9i+4mHq5uzLYyzTnDycHHEWZu4PMEDe6dl9W0IWzfm/F6FV+iNUaRDvm50Z8EPfRPeE8XXkSrTc+M7cZVeUwUVHrSGSgWBPn3JrFh1kx/+y2SCOLd4egT29aQxA8uXhcrGk8WAl1Gb915eSDVGKKNJHgVziuBT6BA9df/AwQ8w7Ta+4iNBR6oAZWjDLpQtHw7jWx2AlbJ1CXhy5lmQuL7lz43/Zuesta3Gnoou8VMDAHDMuN8hcpFmNCCsNfQRkiBMt2jnibPqMHV1xdpIOda329ZvmtINKDATf+tEmna9g1gFKBt2LOUWncTjU0s67peIAKMC+PnoCnoKB73wm7cD29ePa5yri3515tVTRWHPC0iVRxLORNE2/tJICRcBCwf/sVFtu8S2iWLUfhgfBLVns40oX2R9aGjmhUpNXW/wgw5S1OS2UPMG6fJOsvEPKuZgs7SP+bFiLg9qSW4xM+Kll1/Wp6mdpaukJJISwiHOtV/R5MyM76CO1GFr+b7YqAeCvThc2eNym1cm0Sk87iwvkP6WCf+1+vhqXT+yMnnf6zoNr7x6zQjqAokv52OgZGmbBXkBOuWy9W21Dldn7jiaJQohjInKqU4Vd8UHVAXofTMdjmq0Iij5WWsjGhV/"
    # user = database.get_user_by_name("ahoj")
    # user.data = data
    # database.update_user(user)
    
    #verify
    # username1 = input("username: ")
    # password1 = input("password: ")
    # isverified = verify_password(username1,password1)
    # print(isverified)

    authorized = False
    #SWITCH 
    message = server.receive_data_AES(True)
    if isinstance(message,str) and "<DEFAULTLOGIN>" in message:
        authorized,username = DefaultLogin()
    elif isinstance(message,str) and "<REGISTRATION>" in message:
        create_user()
    # elif isinstance(message,str) and "<FACEAUTH>" in message:
    #     authorized, username = Detect_Faces()
    elif isinstance(message,str) and "<FACEREGISTER>" in message:
        username = receive_faceloginData()

        
        pass


    if authorized:
        user = database.get_user_by_name(username)
        data = user.data
        server.send_data_AES(data)
        print("authorized")

    while True:
        data = server.receive_data_AES(True)

        if data is not None:
            print("dtaaa")   
            user = database.get_user_by_name(username)
            user.data = data
            database.update_user(user)



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