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
from ecdsa import NIST384p, VerifyingKey
import string
import os

def receive_faceloginData(server,database):
    username = server.receive_data_string_AES()
    print(f"Face registration for user {username}")
    user = database.get_user_by_name(username)
    Id = user.id
    data = server.receive_data_bytes_AES()
    pictures = pickle.loads(data)

    for i,face in enumerate(pictures):
        if isinstance(face,str):
            pass
        else:
            cv2.imwrite(f"faces\{username}.{Id}.{i+1}.jpg", face)
    end = server.receive_data_string_AES()
    if isinstance(end,str) and "<ENDFACEREGISTER>" in end:
        Server_LearnFace.TrainImages(Id,username)

def Detect_Faces(server,database):
    while True:
        server.send_data_string_AES("TAG")
        username = server.receive_data_string_AES()
        print(f"Face login for user {username}")
        user = database.get_user_by_name(username)
        Id = user.id
        faces = server.receive_data_bytes_AES()
        faces = pickle.loads(faces)
        bol = Server_DetectFace.DetectFace(faces,username,Id)
        if bol == False:
            server.send_data_string_AES("<AGAIN>")
            message = server.receive_data_string_AES()
            if isinstance(message,str) and "<OK>" in message:
                continue
        if bol == True:
            server.send_data_string_AES("<AUTHORIZED>")
            print(f"User {username} is authorized")
            return True, username
        else:
            return False, "notusername"
    
def credibility(username,server,database):
    user = database.get_user_by_name(username)
    verified_signed_data = False
    user_verifying_key = user.user_certificate
    user_verifying_key = VerifyingKey.from_pem(user_verifying_key.encode())
    device_verifying_key = server.receive_data_bytes_AES()
    hash_sig = server.receive_data_bytes_AES()

    #true or false
    verified_device_key = user_verifying_key.verify(hash_sig, device_verifying_key)
    device_verifying_key = VerifyingKey.from_pem(device_verifying_key)

    if device_verifying_key:
        alphabet = string.ascii_letters
        random_string = ''.join(random.choice(alphabet) for i in range(100))
        server.send_data_string_AES(random_string)
        signed_data = server.receive_data_bytes_AES()
        #true or false, pokud plati tak mame hotove overeni ze data client spravne podepsal.
        verified_signed_data = device_verifying_key.verify(signed_data,random_string.encode())
    return verified_signed_data


def DefaultLogin(server,database):
    while True:
        authorized = False
        username, password = server.receive_data_string_AES().split("<>")
        print(f"User {username} is trying to Log in")
        user = database.get_user_by_name(username)
        if user is not None and verify_password(username, password,database):
            server.send_data_string_AES("<ISUSER>")
        else:
            server.send_data_string_AES("<NOUSER>")
            continue

        #credibility
        verified_signed_data = credibility(username,server,database)

        if verified_signed_data and verify_password(username, password,database):
            server.send_data_string_AES("<PASSWORDVERIFIED>")
        else:
            server.send_data_string_AES("<NOPASSWORDVERIFIED>")
            continue

        if verified_signed_data and verify_password(username, password,database):
            print(f"User {username} is on verified device and entered correct password")

            user = database.get_user_by_name(username)
            totp_exits = user.totp
            if totp_exits is None: totp = False
            else: totp = True

            directory = os.listdir("TrainData")
            for fname in directory:
                if os.path.isfile("TrainData" + os.sep + fname):
                    if username in fname:
                        face = True
                        break
                    else:  face = False
                else: face = False

            print(f"User {username} has these authentication methods available: TOTP: {totp}, Face authentization: {face}")
            server.send_data_string_AES(f"{face}<>{totp}")
        else: 
            print(f"User {username} entered wrong password or wrong username") 
            server.send_data_string_AES("Wrong password or username")
            continue
        
        choice = int(server.receive_data_string_AES())

        print(f"User {username} used this authentication methos: {choice} (1.Face authentication, 2. TOTP)")
        if choice == 1:
            #FACE part
            message = server.receive_data_string_AES()
            if isinstance(message,str) and "<FACEAUTH>" in message:
                authorized, username = Detect_Faces(server,database)
        #TOTP
        elif choice == 2:
            #TOTP part
            totp_code = server.receive_data_string_AES()
            totp_db = user.totp
            totp_now = pyotp.TOTP(totp_db).now()
            if int(totp_code) == int(totp_now):
                print(f"User entered correct TOTP key")
                authorized = True
        if authorized:
            server.send_data_string_AES("<AUTHORIZED>")
            return True, username
        else:
            server.send_data_string_AES("<NOTAUTHORIZED>")
            return False, "notauthorized"
        
#tvorba hesla
def passGen(username,password,database):
    print(f"Generating password for user {username}")
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

#overeni hesla
def verify_password(user, password,database):
    print(f"Verifing password for user {user}")
    key_size = 128
    user = database.get_user_by_name(user)
    iteration = user.iteration
    salt = user.salt
    key = PBKDF2(password, salt, dkLen=key_size, count=iteration, hmac_hash_module=SHA256)
    return user.hash == key

#vytvoreni uzivatele
def create_user(server,database):
    print("Creating user")
    username, password, email, AES_password = server.receive_data_string_AES().split("<>")
    user = database.get_user_by_name(username)
    if user is None:
        user = User(username=username, email=email, aes_password=AES_password)
        database.add_user(user)
        passGen(username,password,database)
        server.send_data_string_AES("<USERCREATED>")

        #receive empty data encrypted
        data = server.receive_data_string_AES()
        user = database.get_user_by_name(username)
        user.data = data
        database.update_user(user)
        
        #receive certificate and save
        vk = server.receive_data_string_AES()
        user = database.get_user_by_name(username)
        user.user_certificate = vk
        database.update_user(user)

        choice = server.receive_data_string_AES()
        if choice == "1":
            create_TOTP(username,server,database)
        elif choice == "2":
            message = server.receive_data_string_AES()
            receive_faceloginData(server,database)
        print(f"User {username} created")
    else:
        print("User exists, not created")
        server.send_data_string_AES("<USERNOTCREATED>")

#tvorba TOTP
def create_TOTP(username,server,database):
    print(f"Generating TOTP for user {username}")
    random_bytes = secrets.token_bytes(20)
    base32_string = base64.b32encode(random_bytes).decode()
    totp_seed = base32_string[:16]
    user = database.get_user_by_name(username)
    user.totp = totp_seed
    database.update_user(user)
    server.send_data_string_AES(totp_seed)

#decrypts by chunks
def chunker(cipher,public_key_client_RSA):
    chunk_size = 256 # maximum length of ciphertext that can be decrypted is 256 bytes
    plaintext = b''
    for i in range(0, len(public_key_client_RSA), chunk_size):
        chunk = public_key_client_RSA[i:i+chunk_size]
        plaintext += cipher.decrypt(chunk)
    return plaintext

def run_procces(server):
    print(f"New Connection from {server.host}")
    server.import_RSA()
    server.send_keys_RSA()

    public_key_client_RSA = server.receive_data()
    cipher = PKCS1_OAEP.new(server.rsa_private_key)
    plaintext = chunker(cipher,public_key_client_RSA)
    public_client_RSA = RSA.importKey(plaintext)
    server.countDH(public_client_RSA,server.rsa_private_key)
    database = Database("DATABASE")
  
    while True:
        authorized = False
        #receive register for login or sign up
        login_signup = server.receive_data_string_AES()
        if login_signup == "1":
            authorized, username = DefaultLogin(server,database)
        elif login_signup == "2":
            create_user(server,database)
        else:
            continue

        if authorized:
            choice = server.receive_data_string_AES()
            if choice == "1":
                #access data
                user = database.get_user_by_name(username)
                data = user.data
                server.send_data_string_AES(data)
                print("authorized")
            elif choice == "2":
                #check which method he has
                user = database.get_user_by_name(username)
                totp_exits = user.totp
                if totp_exits is None: totp = False
                else: totp = True

                directory = os.listdir("TrainData")
                for fname in directory:
                    if os.path.isfile("TrainData" + os.sep + fname):
                        if username in fname:
                            face = True
                            break
                        else:  face = False
                    else: face = False

                server.send_data_string_AES(f"{totp}<>{face}")

                method = server.receive_data_string_AES()

                if method == "1":
                    create_TOTP(username,server,database)
                elif method == "2":
                    server.receive_data_string_AES()
                    receive_faceloginData(server,database)

            elif choice == "3":
                user = database.get_user_by_name(username)
                AES_password = user.aes_password
                server.send_data_string_AES(AES_password)
                #pass recovery
        
            while True:
                data = server.receive_data_string_AES()
                if data is not None:
                    print("dtaaa")   
                    user = database.get_user_by_name(username)
                    user.data = data
                    database.update_user(user)
                    break
        else:
            print("Not authorized")
            continue