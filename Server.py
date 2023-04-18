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
import pickle
import Server_LearnFace
import Server_DetectFace
from Database import Database
from Database import User
import pyotp
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import secrets

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
        print("Authenticated by password")
#TODO koukne do DB jaky metody ma
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

    

def verify_password(user, password):
    key_size = 128
    user = database.get_user_by_name(user)
    iteration = user.iteration
    salt = user.salt
    key = PBKDF2(password, salt, dkLen=key_size, count=iteration, hmac_hash_module=SHA256)
    return user.hash == key


def create_user():
    username, password, email, AES_password = server.receive_data_AES(True).split("<>")
    user = database.get_user_by_name(username)
    if user is None:
        user = User(username=username, email=email, aes_password=AES_password)
        database.add_user(user)
        passGen(username,password)
        server.send_data_AES("User Created")
        #CRETIBILITY

        #receive empty data encrypted
        data = server.receive_data_AES(True)
        user = database.get_user_by_name(username)
        user.data = data
        database.update_user(user)

        #receive certificate and save
        vk = server.receive_data_AES(True)
        user = database.get_user_by_name(username)
        user.user_certificate = vk
        database.update_user(user)

        choice = server.receive_data_AES(True)
        if choice == "1":
            create_TOTP(username)
        elif choice == "2":
            message = server.receive_data_AES(True)
            receive_faceloginData()
    else:
        print("user exists, NOT created")
        #server.send_data_AES("User NOT Created")


def create_TOTP(username):
    random_bytes = secrets.token_bytes(20)
    base32_string = base64.b32encode(random_bytes).decode()
    totp_seed = base32_string[:16]
    user = database.get_user_by_name(username)
    user.totp = totp_seed
    database.update_user(user)
    server.send_data_AES(totp_seed)




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
    database = Database("PasswordDB")
  
    while True:
        authorized = False
        #SWITCH 
        #receive register for login or sign up
        login_signup = server.receive_data_AES(True)
        if login_signup == "1":
            authorized, username = DefaultLogin()
        elif login_signup == "2":
            create_user()

        if authorized:
            choice = server.receive_data_AES(True)
            if choice == "1":
                #access data
                user = database.get_user_by_name(username)
                data = user.data
                server.send_data_AES(data)
                print("authorized")
            elif choice == "2":
                #add method
                #check which method he has
                totp = True
                face = False

                server.send_data_AES(f"{totp}<>{face}")

                method = server.receive_data_AES(True)

                if method == "1":
                    create_TOTP(username)
                elif method == "2":
                    server.receive_data_AES(True)
                    receive_faceloginData()



            elif choice == "3":
                user = database.get_user_by_name(username)
                AES_password = user.aes_password
                server.send_data_AES(AES_password)
                #pass recovery
            

            while True:
                data = server.receive_data_AES(True)
                if data is not None:
                    print("dtaaa")   
                    user = database.get_user_by_name(username)
                    user.data = data
                    database.update_user(user)
                    break

        else:
            print("Not authorized")