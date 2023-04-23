import Client_session
from Client_ReadFace import FaceCapturer
import Client_DetectFace
from Shell import KryPiShell
import Encryption_AES
import json
from getpass import getpass
import CA
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from ecdsa import SigningKey, NIST384p
import TOTP
from Crypto.Hash import SHA256
import secrets
import string
import re

""" Description: A function used to create authentication using your face
    Parameters: str : username -> the user to whom the face authentication is added"""
def Face_Registration(username):
    Read_face = FaceCapturer()
    input("Program will now scan your face. Press ENTER to continue")
    images = Read_face.capture_images(username)
    client.send_data_string_AES("<FACEREGISTER>")
    client.send_data_string_AES(username)
    client.send_data_bytes_AES(images)
    client.send_data_string_AES("<ENDFACEREGISTER>")

""" Description: A function used to authenticate user by facedetection, client side will scan face of the user and sand that data to server to authenticate
    Parameters: str : name -> the user that will be authenticated by facedetection
    Returns: boolean -> if the user is authenticated or not"""
def Face_login(name):
    print("Face authentication login")
    client.send_data_string_AES("<FACEAUTH>")
    while True:
        try:
            client.receive_data_string_AES()
            client.send_data_string_AES(name)
            input("Program will now start scanning your face. Press ENTER to continue.")
            clients_face = Client_DetectFace.DetectFace()
            client.send_data_bytes_AES(clients_face)
            message = client.receive_data_string_AES()
            if isinstance(message,str) and "<AGAIN>" in message:
                print("Server didnt recognized the user, scanning for faces again.")
                client.send_data_string_AES("<OK>")
                continue
            if isinstance(message,str) and "<AUTHORIZED>" in message:
                return True 
            
        except KeyboardInterrupt:
            print("Scanning ended, Face authentication now saved.")
            return False

""" Description: A function used to reccive TOTP authentication method for user, the function recive TOTP seed and display it to user by SEED and QR code
    Parameters: str : username -> the user to whom the TOTP authentication is added
    """
def totp_registration(username):
    totp_seed = client.receive_data_string_AES()
    print("QR code of your TOTP seed")
    TOTP.totp_generate_qrcode(totp_seed,username)
    print(f"Your's TOTP_seed is: {totp_seed}")

""" Description: Function which is used to verify the trustworthiness of the device, the client sends the public DSA key and the signed hash.sig file to the server, then receives random data from the server, which it signs and the server verifies that it is communicating with the correct authenticated client.
    Parameters: str : username -> the user whom credibility is beeing check
    Returns: boolean -> if the user is trustworthy or not
    """
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
        temp = hash_signature.read()
        client.send_data_bytes_AES(temp)
        print(len(temp))
        print(type(temp))

    random_data = client.receive_data_string_AES()
    random_data = random_data.encode()
    signed_data = sig.sign(random_data)
    client.send_data_bytes_AES(signed_data)
    return True
""" Description: Function that is used for generating pair of keys for Verification of user.
    Parameters: str : password -> the password for pem file
                str : username -> username of the user
    Returns: pem : vk -> public key of the user
    """
def create_certificate(password,username):
    sk = SigningKey.generate(curve=NIST384p)  # uses NIST192p
    vk = sk.verifying_key
    with open(f"public_key_{username}.pem", 'wb') as public_key:
        public_key.write(vk.to_pem())
    with open(f"private_key_{username}.pem", 'wb') as private_key:
        private_key.write(CA.encrypt(password.encode(), sk.to_pem()))
    return vk.to_pem()

""" Description: Function that check if the format of email is corect by regex
    Parameters: str : email -> the email that is being checked
    Returns: boolean -> True if the email is valid, False if not
    """
def is_valid_email(email):
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9.%+-]+@[a-zA-Z0-9.-]+.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return True
    else:
        return False

""" Description: Function used to create a user, the user enters name, password, email and vault key. A backup password is created for the recovery vault key. This information is then sent to the server. Next, an empty password database is created and this is also sent encrypted to the server, along with the user's public key for confidentiality verification. Finally, the user can choose whether they want to authenticate using TOTP or FaceDetection.
    Returns: boolean -> False if the user is allready in database or is not created
    """
def Register():
    #TODO here i want AES KEY idk if generater or what
    while True:
        username = input("Enter username:")
        if len(username) < 5 or username[0].isdigit() == True:
            print("Wrong Username, At least 6 characters long and dont begin with number!!!")
        else: break
    while True:
        password = getpass("Enter password:")
        if len(password) < 3:
            print("Wrong Password, At least 3 characters long.")
        else: break
    while True:
        e_mail = input("Enter email:")
        if is_valid_email(e_mail): break
    while True:
        decrypt_key = getpass("Enter vault d/encryption phrase: ")
        if len(password) > 3: break
        else: print("Wrong decrypt key")

    decrypt_key_hash = SHA256.new(decrypt_key.encode()).digest()
    recovery_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(20))

    input("!! Your vault recovery key will be show, make sure noone sees it. To continue press ENTER")
    print(f"""
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            This is your vault recovery key:
                {recovery_string}
(save it somewhere save, you will need it for recovery)
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

""" Description: Function used for user login. It sends username and password to the server and calls the function for authentication of the device. If login and trust is OK, it finds out the two factor authentication options from the server and selects one of them.
    Returns: boolean + str : username -> True if the user is authenticated and verified, username of the user that has been verified and authenticated
    """
def DefaultLogin():
    while True:
        username = input("Username: ")
        pasw = getpass("Password: ")
        client.send_data_string_AES(f"{username}<>{pasw}")
        message = client.receive_data_string_AES()
        if "<NOUSER>" in message:
            print("NO user by this name exists")
            continue
        #credibilty
        bol = credibility(username)

        message = client.receive_data_string_AES()
        if "<PASSWORDVERIFIED>" in message:
            print("Your password is verified and device is verified")

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

""" Description: Function used for input of user, user can Login or Sign up
    Returns: boolean + str : username -> True if the user is authenticated and verified, username of the user that has been verified and authenticated
    """
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

""" Description: That is used for vault key recovery, server send Encrypted vault key by recovery key to user, he will decrypt it and display vaul key.
    """
def password_recovery():
    AES_password = client.receive_data_string_AES()
    recovery_phrase = input("Recovery phrase: ")
    hashed_recovery_key = SHA256.new(recovery_phrase.encode()).digest()
    print(hashed_recovery_key)
    AES_password = Encryption_AES.decrypt(AES_password, hashed_recovery_key)
    print(AES_password)
#TODO pregenerovani a vytvoreni noveho recovery klice

""" Description: Function that is used for interaction with user when is he logged to the server and is Authenticated and Verified. The user can choose from Accesing data, Adding or refreshing TwoFactorAuth and password recovery.
    Parameters: str : username -> the username of the logged user
    """
def user_interface(username):
    while True:
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
            continue


""" 
Description: MAIN function that will connect user to server, Verify the server and count the ECDH shared key for Encrypted communication.
"""
if __name__ == '__main__':
    authorized = False
    try:
        # select servers address and port
        client = Client_session.Client("localhost",8080)
        client.connect()
        key, hash = client.recieve_RSA()
        verified = client.verify_signature(key,hash)
        if verified:
            client_RSA_key = client.gen_RSA()
            public_RSA_server_key = RSA.importKey(key)
            cipher = PKCS1_OAEP.new(public_RSA_server_key)
            temp = client_RSA_key.public_key().exportKey()

            chunk_size = 190 # maximum length of plaintext that can be encrypted is 214 bytes
            ciphertext = b''
            for i in range(0, len(temp), chunk_size):
                chunk = temp[i:i+chunk_size]
                ciphertext += cipher.encrypt(chunk)
            client.send_data(ciphertext)

            client.countDHEC(public_RSA_server_key,client_RSA_key)
        while True:
            authorized, username = Select()

            #if authentiation was succesfull
            if authorized == True:
                user_interface(username)
            else:
                print("not authorized")
                continue

    except KeyboardInterrupt:
        print("No data saved. Changes made were lost.")
        print("Exiting....")
