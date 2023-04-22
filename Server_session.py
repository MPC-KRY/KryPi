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

    def send_data_string_AES(self, data):
        if self.conn is not None:
            data = Encryption_AES.encrypt(data, self.ECDH_key)
            NetworkUtils.send_row(self.conn, data.encode())

    def send_data_bytes_AES(self,data):
        if self.conn is not None:
            data = Encryption_AES.encrypt2(data, self.ECDH_key)
            NetworkUtils.send_row(self.conn, data)

    def receive_data(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            return data

    def receive_data_string_AES(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            if len(data) != 0:
                mes = Encryption_AES.decrypt(data.decode(), self.ECDH_key)
                return mes

    def receive_data_bytes_AES(self):
        if self.conn is not None:
            data = NetworkUtils.recv_row(self.conn)
            if len(data) != 0:
                mes = Encryption_AES.decrypt2(data.decode(), self.ECDH_key)
                return mes

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

