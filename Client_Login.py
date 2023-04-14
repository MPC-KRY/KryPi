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
    #Face_Registration()
    client.send_data_AES("<REGISTRATION>")
    username = input("Enter username:")
    password = input("Enter password:")
    e_mail = input("Enter email:")
    client.send_data_AES(f"{username}<>{password}<>{e_mail}")

    message = client.receive_data_AES()
    print(message)


    pass


def Login():
    pass

def DefaultLogin():
    user = input("username")
    pasw = input("password")
    client.send_data_AES("<DEFAULTLOGIN>")
    client.send_data_AES(f"{user}<>{pasw}")
    try:
        face,totp = client.receive_data_AES().split("<>")

        face = True if face == "True" else False
        totp = True if totp == "True" else False
    except:
        message = client.receive_data_AES()
        print(message)

    if face:
        print("je tam oblicej")
    if totp:
        print("je tam totp")
        choice = input("choose authentication type 1. face, 2.totp")

    client.send_data_AES(choice)
        
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
        print("""

            1. Face authentication (only working)
            2. Name and Password + TOTP
            3.registration
            4. 
        """)
        register = input("Select type of login authentication: ")
        if register == "1":
            #face authorization
            print("face authorization authentication")
            Face_login()
            break
        elif register == "2":
            print("TOTP authentication")
            authorized = DefaultLogin()
        elif register == "3":
            print("user registration registration")
            Register()
            print("registration complete")
            break
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
        authorized = Select()
        authentication = True
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
