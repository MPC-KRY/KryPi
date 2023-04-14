import Client
from Client_ReadFace import FaceCapturer
import Client_DetectFace
from Test import KryPiShell
import test_AES
import json
import getpass




def Face_Registration():
    Read_face = FaceCapturer()
    name, images = Read_face.capture_images()
    client.send_data_AES("<STARTFACELOGIN>")
    client.send_data_AES(f"<BEGIN>{name}")
    client.send_data_AES("<SEPARATOR>")
    client.send_pictures_AES(images)
    client.send_data_AES("<DEPARATOR>")
    client.send_data_AES("<ENDFACELOGIN>")


def Face_login():

    client.send_data_AES("<STARTFACE>")
    while True:
        try:
            client.receive_data_AES()
            name = input("Input your name:")
            client.send_data_AES(name)
            clients_face = Client_DetectFace.DetectFace()
            client.send_pictures_AES(clients_face)
            message = client.receive_data_AES()
            print(message + "AGAIN MEASGE")
            if isinstance(message,str) and "<AGAIN>" in message:
                client.send_data_AES("<OK>")
                Face_login()
            if isinstance(message,str) and "<AUTHORIZED>" in message:
                return True
                
            
        except KeyboardInterrupt:
            print("ended")
            break


def Register():
    Face_Registration()

def Login():
    pass

def DefaulLogin():
    user = input("username")
    pasw = input("password")


    




def Select():

    while True:
        print("""
            Welcome to out Cryptography project.
            This is Login page, where you have to authorize to access your
            saved entries
            Or you can recover your password

            Available logins
            1. Face authentication (only working)
            2. Name and Password + TOTP
            3. Name and Password + Face authentication
            4. 
            Login or Recover password (here will be choice)
        """)
        register = input("Select type of login authentication: ")
        if register == "1":
            #face authorization
            print("face authorization authentication")
            Face_login()
            break
        elif register == "2":
            print("Name and password authentication")
            DefaultLogin()
            break
        elif register == "3":
            print("FaceLogin registration")
            Register()
            print("registration complete")
            break
        else:
            print("not correct choice")






if __name__ == '__main__':
    print("*****************************************")
    print("*        WELCOME TO THE LOGIN SCREEN     *")
    print("*****************************************")
    print("| 1. Login                              |")
    print("| 2. Password recovery                  |")
    print("-----------------------------------------")
    option = input("Enter your choice (1/2): ")
    try:
        client = Client.Client()
        client.connect()
        Select()
        authentication = True
        #if authentiation was succesfull
        if authentication == True:
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

    except KeyboardInterrupt:
            data = krypi.retrieve_data()
            client.send_data_AES(test_AES.encrypt(json.dumps(data), client.AES_key))
            print("Exiting....")
