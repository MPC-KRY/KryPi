import socket
import binascii
import NetworkUtils
import Encryption_AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import load_der_public_key
import threading
import Server_functions


""" 
Description: This is the Server class, for creating the server object. It is used for running the server, sending and recieving plaintext or encrypted data. And importing/encrypting RSA, generating ECDH.
"""
class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()
        
    def start(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        print("Server started on {}:{}".format(self.host, self.port))
        
        while True:
            conn, addr = self.socket.accept()
            new_thread = ClientThread(conn, addr)
            new_thread.start()


class ClientThread(threading.Thread):
    def __init__(self,conn,host):
        threading.Thread.__init__(self)
        self.host = host
        self.socket = None
        self.conn = conn
        self.ECDH_key = None
        self.rsa_private_key = None
        self.rsa_public_key = None
        self.rsa_hash_sig_key = None


    """
    Description: Function that is run everytime new client connects.
    """
    def run(self):
        Server_functions.run_procces(self)

    """ 
    Description: Send plaintext data
    Parameters: data -> data that will be send
    """
    def send_data(self, data):
        if self.conn is not None:
            NetworkUtils.send_row(self.conn, data)

    """ 
    Description: Send AES encrypted data 
    Parameters: data -> string data that will be send
    """
    def send_data_string_AES(self, data):
        if self.conn is not None:
            data = Encryption_AES.encrypt(data, self.ECDH_key)
            NetworkUtils.send_row(self.conn, data.encode())

    """ 
    Description: Send AES encrypted data 
    Parameters: data -> bytes data that will be send
    """
    def send_data_bytes_AES(self,data):
        if self.conn is not None:
            data = Encryption_AES.encrypt2(data, self.ECDH_key)
            NetworkUtils.send_row(self.conn, data)

    """ 
    Description: Receive plaintext data 
    """
    def receive_data(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            return data

    """ 
    Description: Receive string AES Encrypted data
    """
    def receive_data_string_AES(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            if len(data) != 0:
                mes = Encryption_AES.decrypt(data.decode(), self.ECDH_key)
                return mes

    """ 
    Description: Receive bytes AES Encrypted data
    """
    def receive_data_bytes_AES(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            if len(data) != 0:
                mes = Encryption_AES.decrypt2(data.decode(), self.ECDH_key)
                return mes

    def close(self):
        self.sock.close()

    """ 
    Description: Used for reading RSA public, private keys and signed data.
    """
    def import_RSA(self):
        with open("private_key_RSA.pem", 'rb') as private_key_file:
            self.rsa_private_key = RSA.importKey(private_key_file.read())

        with open("public_key_RSA.pem", 'rb') as public_key_file:
            self.rsa_public_key = public_key_file.read()

        with open("hash.sig", 'rb') as hash_file:
            self.rsa_hash_sig_key = hash_file.read()

    """ 
    Description: Send RSA public key and signed hash.
    """
    def send_keys_RSA(self):
        self.send_data(self.rsa_public_key)
        self.send_data(self.rsa_hash_sig_key)

    def decrypt_RSA(self,data):
        return self.rsa_private_key.decrypt(data)

    """ 
    Description: A shared key is negotiated between the server and the client for AES communication. Shared parameters are encrypted by RSA.
    Parameters: pub_key_server -> RSA server public key
                priv_key_client -> RSA client private key
    """
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
        print(f"\nSession's {str(self.host)} derived key: {binascii.b2a_hex(Bob_derived_key).decode()}", )


if __name__ == '__main__':
    """
    Description: Main Function, that is user to start Server of database.
    Parameters: str : addr -> address on which will the server function.
                int : port -> port on which will the server function.
    """
    server = Server("localhost",8080)
    server.start()