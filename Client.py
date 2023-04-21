import Client_session
from Client_ReadFace import FaceCapturer
import Client_DetectFace
from Shell import KryPiShell
import Encryption_AES
import json
import getpass
import CA
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from ecdsa import SigningKey, NIST384p, VerifyingKey
import TOTP
from Crypto.Hash import SHA256
import secrets
import string
import re


def Face_Registration(username):
    Read_face = FaceCapturer()
    images = Read_face.capture_images(username)
    client.send_data_string_AES("<FACEREGISTER>")
    client.send_data_string_AES(username)
    client.send_data_bytes_AES(images)
    client.send_data_string_AES("<ENDFACEREGISTER>")


def Face_login(name):
    client.send_data_string_AES("<FACEAUTH>")
    while True:
        try:
            client.receive_data_string_AES()
            client.send_data_string_AES(name)
            clients_face = Client_DetectFace.DetectFace()
            client.send_data_bytes_AES(clients_face)
            message = client.receive_data_string_AES()
            print(message + "AGAIN MEASGE")
            if isinstance(message,str) and "<AGAIN>" in message:
                client.send_data_string_AES("<OK>")
                Face_login()
                return False
            if isinstance(message,str) and "<AUTHORIZED>" in message:
                return True 
            
        except KeyboardInterrupt:
            print("ended")
            break

# TODO dodelat

def totp_registration(username):
    totp_seed = client.receive_data_string_AES()
    print("QR code of your TOTP seed")
    TOTP.totp_generate_qrcode(totp_seed,username)
    print(f"Your's TOTP_seed is: {totp_seed}")




def credibility(username):
    password = input("Input your certificate password: ")
    # uzivatel si open vygeneruje dalsi par klicu
    sig = None
    key = None

    with open(f"private_key_DSA_{username}.pem", 'rb') as private_key:
        try:
            sig = SigningKey.from_pem(CA.decrypt(password.encode(), private_key.read()))
            key = sig.verifying_key
            send_key = key.to_pem()
            client.send_data_bytes_AES(send_key)
        except Exception:
            client.send_data_bytes_AES("<ERROR>".encode())
            return False
            
    with open(f"hash_{username}_verify.sig", 'rb') as hash_signature:
        client.send_data_bytes_AES(hash_signature.read())

    random_data = client.receive_data_string_AES()
    random_data = random_data.encode()
    signed_data = sig.sign(random_data)
    client.send_data_bytes_AES(signed_data)
    return True

def create_certificate(password,username):
    sk = SigningKey.generate(curve=NIST384p)  # uses NIST192p
    vk = sk.verifying_key
    with open(f"public_key_{username}.pem", 'wb') as public_key:
        public_key.write(vk.to_pem())
    with open(f"private_key_{username}.pem", 'wb') as private_key:
        private_key.write(CA.encrypt(password.encode(), sk.to_pem()))
    return vk.to_pem()


def is_valid_email(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return True
    else:
        return False


def Register():
    #TODO here i want AES KEY idk if generater or what
    while True:
        username = input("Enter username:")
        if len(username) < 5 or username[0].isdigit() == True:
            print("Wrong Username, At least 6 characters long and dont begin with number!!!")
        else: break
    while True:
        password = input("Enter password:")
        if len(password) < 3:
            print("Wrong Password, At least 3 characters long.")
        else: break
    while True:
        e_mail = input("Enter email:")
        if is_valid_email(e_mail): break
    while True:
        decrypt_key = input("Enter vault d/encryption phrase: ")
        if len(password) > 3: break
        else: print("Wrong decrypt key")


    decrypt_key_hash = SHA256.new(decrypt_key.encode()).digest()
    recovery_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))
    print(f"""
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            This is your vault recovery key:
                {recovery_string}
        (save it somewerher you wil use this for vault recovery)
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """)

    hashed_recovery_key = SHA256.new(recovery_string.encode()).digest()
    AES_password = Encryption_AES.encrypt(decrypt_key, hashed_recovery_key)

    client.send_data_string_AES(f"{username}<>{password}<>{e_mail}<>{AES_password}")
    
    message = client.receive_data_string_AES()
    if isinstance(message,str) and "<USERCREATED>" in message:
        print("User was created")
    elif isinstance(message,str) and "<USERNOTCREATED>" in message:
        print("User not create, user already exists")
        return False
    
    #sending defualt empty data into data section
    data = "[]"
    data = Encryption_AES.encrypt(data, decrypt_key_hash)
    client.send_data_string_AES(data)

#TODO pripadne prespsat at posila bytes not sting
    # creation of certificate
    print("Creating certificate")
    vk = create_certificate(password, username)
    client.send_data_string_AES(vk.decode())

    choice = input("Do you want to setup 1. TOTP or 2.Face")
    client.send_data_string_AES(choice)
    choice = int(choice)
    if choice == 1:
        totp_registration(username)
    elif choice == 2:
        #register FACE
        Face_Registration(username)
    
def DefaultLogin():
    while True:
        username = input("Username: ")
        pasw = input("Password: ")
        client.send_data_string_AES(f"{username}<>{pasw}")
        message = client.receive_data_string_AES()
        if "<NOUSER>" in message:
            print("NO user by this name exists")
            continue
        #credibilty
        bol = credibility(username)

        message = client.receive_data_string_AES()
        if "<PASSWORDVERIFIED>" in message:
            print("You are password verified and device verified")

            face,totp = client.receive_data_string_AES().split("<>")
            face = True if face == "True" else False
            totp = True if totp == "True" else False

            while True:
                if face and totp:
                    choice = input("Available authentication type 1. face, 2.totp")
                    if choice != "1" or choice != "2":
                        print("Wrong decivsion again")
                        continue
                    else: break

                elif face:
                    choice = input("Available authentication type 1. face")
                    if choice != "1":
                        print("Wrong decivsion again")
                        continue
                    else: break

                elif totp:
                    choice = input("Available authentication type 2. totp")
                    if choice != "2":
                        print("Wrong decivsion again")
                        continue
                    else: break
                else: continue

            client.send_data_string_AES(choice)
            if int(choice) == 1:
                message = Face_login(username)
            if int(choice) == 2:
                totp_code = input("Insert TOTP code: ")
                client.send_data_string_AES(totp_code)

            message = client.receive_data_string_AES()
            if isinstance(message,str) and "<AUTHORIZED>" in message:
                return True, username
            else: 
                return False, "notusername"
        else:
            print("wrong pass or username")
            continue

def Select():
    while True:
        authorized = True
        print("""
            1. Name and Password + (Face/TOTP)
            2. User creation
        """)
        register = input("Select type of login authentication: ")
        client.send_data_string_AES(register)
        if register == "1":
            print("Authentication")
            authorized,username = DefaultLogin()
            return authorized,username
        elif register == "2":
            print("user registration")
            Register()
            continue
        else:
            print("not correct choice")
            continue


def password_recovery():
    AES_password = client.receive_data_string_AES()
    recovery_phrase = input("Recovery phrase: ")
    hashed_recovery_key = SHA256.new(recovery_phrase.encode()).digest()
    print(hashed_recovery_key)
    AES_password = Encryption_AES.decrypt(AES_password, hashed_recovery_key)
    print(AES_password)
#TODO pregenerovani a vytvoreni noveho recovery klice

def user_interface(username):
    #if authentiation was succesfull
    choice = input("1. Acces Data, 2. Add/renew auth. method, 3. pass. recovery")

    client.send_data_string_AES(choice)
    if choice == "1":
        json_data = client.receive_data_string_AES()

        decrypt_key = input("Enter vault decryption phrase:")
        decrypt_key_hash = SHA256.new(decrypt_key.encode()).digest()

        json_data = Encryption_AES.decrypt(json_data, decrypt_key_hash)
        krypi = KryPiShell()
        krypi.add_data(json_data)
        krypi.cmdloop()
        data = krypi.retrieve_data()
        data = Encryption_AES.encrypt(json.dumps(data), decrypt_key_hash)
        client.send_data_string_AES(data)
   
    elif choice == "2":
        #add method
        totp, face = client.receive_data_string_AES().split("<>")
        face = True if face == "True" else False
        totp = True if totp == "True" else False

        if face:
            print("You have face authentication")
        elif totp:
            print("You have TOTP authentication")

        method = input("Method: 1. TOTP, 2. Face: ")   
        client.send_data_string_AES(method)
        if method == "1":
            totp_registration(username)
        elif method == "2":
            Face_Registration(username)

    elif choice == "3":
        password_recovery()
        user_interface(username)










if __name__ == '__main__':
    authorized = False
    try:
        client = Client_session.Client()
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
            #Select()

    except KeyboardInterrupt:
            #TODO expection
            if authorized:
                data = krypi.retrieve_data()
                client.send_data_string_AES(Encryption_AES.encrypt(json.dumps(data), client.AES_key))
                print("Exiting....")
