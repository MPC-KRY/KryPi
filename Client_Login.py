import Client
from Client_ReadFace import FaceCapturer
import Client_DetectFace
from Test import KryPiShell
import test_AES
import json
import getpass
import CA
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP





def Face_Registration():
    Read_face = FaceCapturer()
    name, images = Read_face.capture_images()
    client.send_data_AES("<FACEREGISTER>")
    client.send_data_AES(name)
    client.send_pictures_AES(images)
    client.send_data_AES("<ENDFACEREGISTER>")


def Face_login(name):
    client.send_data_AES("<FACEAUTH>")
    while True:
        try:
            client.receive_data_AES()
            client.send_data_AES(name)
            clients_face = Client_DetectFace.DetectFace()
            client.send_pictures_AES(clients_face)
            message = client.receive_data_AES()
            print(message + "AGAIN MEASGE")
            if isinstance(message,str) and "<AGAIN>" in message:
                client.send_data_AES("<OK>")
                Face_login()
                return False
            if isinstance(message,str) and "<AUTHORIZED>" in message:
                return True
                
            
        except KeyboardInterrupt:
            print("ended")
            break

def totp_registration():
    pass



def Register():
    #Face_Registration()
    client.send_data_AES("<REGISTRATION>")
    username = input("Enter username:")
    password = input("Enter password:")
    e_mail = input("Enter email:")
    client.send_data_AES(f"{username}<>{password}<>{e_mail}")

    message = client.receive_data_AES()
    print(message)


    choice = input("you want to setup totp or face")
    choice = int(choice)
    if choice == 1:
        #TOTP
        pass
    elif choice == 2:
        #register FACE
        Face_Registration()

    #register TOTP



def Login():
    pass

def DefaultLogin():
    username = input("username")
    pasw = input("password")
    client.send_data_AES("<DEFAULTLOGIN>")
    client.send_data_AES(f"{username}<>{pasw}")
    try:
        face,totp = client.receive_data_AES().split("<>")

        face = True if face == "True" else False
        totp = True if totp == "True" else False
    except:
        message = client.receive_data_AES()
        print(message)


    choice = input("Available authentication type 1. face, 2.totp")

    client.send_data_AES(choice)

    if int(choice) == 1:
        message = Face_login(username)

    if int(choice) == 2:
        totp_code = input("insert TOTP code")
        client.send_data_AES(totp_code)

    message = client.receive_data_AES()
    if isinstance(message,str) and "<AUTHORIZED>" in message:
        return True
    else: 
        return False


def Select():
    while True:
        authorized = True
        print("""
            1. Name and Password + 2FA
            2. User creation
            3. Password recovery
        """)
        register = input("Select type of login authentication: ")
        # if register == "1":
        #     #face authorization
        #     print("face authorization authentication")
        #     Face_login()
        #     break
        if register == "1":
            print("Authentication")
            authorized = DefaultLogin()
        elif register == "2":
            print("user registration registration")
            Register()
            print("registration complete")
            break
        elif register == "3":
            pass
        else:
            print("not correct choice")
        return authorized






if __name__ == '__main__':
    print("*****************************************")
    print("*        WELCOME TO THE LOGIN SCREEN     *")
    print("*****************************************")
    print("| 1. Login                              |")
    print("| 2. Password recovery                  |")
    print("-----------------------------------------")
    #option = input("Enter your choice (1/2): ")
    try:
        client = Client.Client()
        client.connect()
        key, hash = client.recieve_RSA()
        verified = client.verify_signature(key,hash)
        if verified:
            client_RSA_key = client.gen_RSA()
            public_RSA_server_key = RSA.importKey(key)
            cipher = PKCS1_OAEP.new(public_RSA_server_key)
            temp = client_RSA_key.public_key().exportKey()

# TODO rozdeleni na chunky
            chunk_size = 190 # maximum length of plaintext that can be encrypted is 214 bytes
            ciphertext = b''
            for i in range(0, len(temp), chunk_size):
                chunk = temp[i:i+chunk_size]
                ciphertext += cipher.encrypt(chunk)
            client.send_data(ciphertext)

        client.countDHEC(public_RSA_server_key,client_RSA_key)
        authorized = Select()

        #if authentiation was succesfull
        if authorized == True:
            json_data = client.receive_data_AES()
            json_data = test_AES.decrypt(json_data, client.AES_key)
            client.add_to_json_data(json_data)
            krypi = KryPiShell()
            krypi.add_data(json_data)
            krypi.cmdloop()

            data = krypi.retrieve_data()
            data = test_AES.encrypt(json.dumps(data), client.AES_key)
            print(data)
            client.send_data_AES(data)
        else:
            print("now authorized")

    except KeyboardInterrupt:
            data = krypi.retrieve_data()
            client.send_data_AES(test_AES.encrypt(json.dumps(data), client.AES_key))
            print("Exiting....")
