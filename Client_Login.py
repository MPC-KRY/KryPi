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
from ecdsa import SigningKey, NIST384p, VerifyingKey
import TOTP



def Face_Registration(username):
    Read_face = FaceCapturer()
    images = Read_face.capture_images(username)
    client.send_data_AES("<FACEREGISTER>")
    client.send_data_AES(username)
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

# TODO dodelat
def totp_registration(username):
    totp_seed = client.receive_data_AES()
    TOTP.totp_generate_qrcode(totp_seed,username)
    print("QR code of your TOTP seed")
    print(f"Your's TOTP_seed is: {totp_seed} (Imput it inside authenticator)")

def credibility(username):
    # uzivatel si open vygeneruje dalsi par klicu
    pass

def create_certificate(password,username):
    sk = SigningKey.generate(curve=NIST384p)  # uses NIST192p
    vk = sk.verifying_key

    with open(f"public_key_{username}.pem", 'wb') as public_key:
        public_key.write(vk.to_pem())
    with open(f"private_key_{username}.pem", 'wb') as private_key:
        private_key.write(CA.encrypt(password.encode(), sk.to_pem()))
    return vk.to_pem()

def Register():
    #TODO here i want AES KEY idk if generater or what
    #Face_Registration()
    client.send_data_AES("<REGISTRATION>")
    username = input("Enter username:")
    password = input("Enter password:")
    e_mail = input("Enter email:")
    client.send_data_AES(f"{username}<>{password}<>{e_mail}")

    message = client.receive_data_AES()
    print(message)

    #sending defualt empty data into data section
    data = "[]"
    data = test_AES.encrypt(data, client.AES_key)
    client.send_data_AES(data)

    # creation of certificate
    print("Creating certificate")
    vk = create_certificate(password, username)
    client.send_data_AES(vk.decode())

    choice = input("you want to setup TOTP or face")
    client.send_data_AES(choice)
    choice = int(choice)
    if choice == 1:
        totp_registration(username)
        
    elif choice == 2:
        #register FACE
        Face_Registration(username)



def Login():
    pass


def DefaultLogin():
    username = input("Username: ")
    pasw = input("Password: ")
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
        return True, username
    else: 
        return False, "notusername"

def specialLogin():
    username = input("Enter your username: ")

    totp_code = input("Please enter TOTP: ")
    client.send_data_AES(totp_code)

    Face_login(username)

    message = client.receive_data_AES() 
    if isinstance(message,str) and "<AUTHORIZED>" in message:
        #TODO here recover password
        return True, username
    else: 
        return False, "notusername"







def Select():
    while True:
        authorized = True
        print("""
            1. Name and Password + (Face/TOTP)
            2. User creation
            3. Face + TOTP aka password recovery
        """)
        register = input("Select type of login authentication: ")
        if register == "1":
            print("Authentication")
            authorized,username = DefaultLogin()
        elif register == "2":
            print("user registration")
            Register()
            Select()
        elif register == "3":
            specialLogin()
            Select()
        else:
            print("not correct choice")
        return authorized,username





def user_interface(username):
    #if authentiation was succesfull
    choice = input("1. Acces Data, 2. Add/renew auth. method, 3. pass. recovery")
    client.send_data_AES(choice)
    if choice == "1":
        json_data = client.receive_data_AES()
        json_data = test_AES.decrypt(json_data, client.AES_key)
        #client.add_to_json_data(json_data)
        krypi = KryPiShell()
        krypi.add_data(json_data)
        krypi.cmdloop()
        data = krypi.retrieve_data()
        data = test_AES.encrypt(json.dumps(data), client.AES_key)
        client.send_data_AES(data)
   
    elif choice == "2":
        #add method
        totp, face = client.receive_data_AES()
        face = True if face == "True" else False
        totp = True if totp == "True" else False

        if face:
            print("You have face authentication")
        elif totp:
            print("You have TOTP authentication")

        method = input("which method 1. totp, 2. face: ")   
        if method == "1":
            Face_Registration(username)
        elif method == "2":
            totp_registration(username)


#TODO password recovery
    elif choice == "3":
        pass






if __name__ == '__main__':
    print("*****************************************")
    print("*        WELCOME TO THE LOGIN SCREEN     *")
    print("*****************************************")
    print("| 1. Login                              |")
    print("| 2. Password recovery                  |")
    print("-----------------------------------------")
    #option = input("Enter your choice (1/2): ")
    authorized = False
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

            #overeni duveryhodnosti


# TODO rozdeleni na chunky
            chunk_size = 190 # maximum length of plaintext that can be encrypted is 214 bytes
            ciphertext = b''
            for i in range(0, len(temp), chunk_size):
                chunk = temp[i:i+chunk_size]
                ciphertext += cipher.encrypt(chunk)
            client.send_data(ciphertext)

        client.countDHEC(public_RSA_server_key,client_RSA_key)
        authorized, username = Select()


        #if authentiation was succesfull
        if authorized == True:
            user_interface(username)


        else:
            print("not authorized")

    except KeyboardInterrupt:
            if authorized:
                data = krypi.retrieve_data()
                client.send_data_AES(test_AES.encrypt(json.dumps(data), client.AES_key))
                print("Exiting....")
