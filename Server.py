import binascii
import json
import socket

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import load_der_public_key

import test_AES


class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
        self.ECDH_key = None

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"server is listening on {self.host}:{self.port}")
        self.conn, addr = self.sock.accept()

    def send_data(self, data):
        if self.conn is not None:
            self.conn.send(data)

    def send_data_AES(self, data):
        if self.conn is not None:
            data = test_AES.encrypt(data, self.ECDH_key)
            self.conn.send(data.encode())
            
    def receive_data(self):
        if self.conn is not None:
            data = self.conn.recv(1024)
            return data

    def receive_data_AES(self):
        if self.conn is not None:
            data = self.conn.recv(1024)
            if len(data) != 0:
                return test_AES.decrypt(data.decode(), self.ECDH_key)
        
    def close(self):
        self.sock.close()

    def countDH(self):

        # accepts the client's public key and creates its own private key
        Alice_public_key_bytes = self.receive_data()
        Bob_private_key = ec.generate_private_key(ec.SECP384R1())

        # converts the ECDH public key to bytes and sends it to the client
        Bob_public_key_bytes = Bob_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.send_data(Bob_public_key_bytes)

        # calculates the secret key
        Alice_public_key = load_der_public_key(Alice_public_key_bytes)
        size = 32
        Bob_shared_key = Bob_private_key.exchange(ec.ECDH(), Alice_public_key)
        Bob_derived_key = HKDF(hashes.SHA256(), size, None, b'', ).derive(Bob_shared_key)

        self.ECDH_key = binascii.b2a_hex(Bob_derived_key)[:32]
        print("\nBob's derived key: ", binascii.b2a_hex(Bob_derived_key).decode())


server = Server()
server.listen()
server.countDH()




def read_json_data(file_path):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_data

with open('myfile.txt', 'r') as file:
    message = file.read()
    file.close()
# json_data = read_json_data('JSON_data.json')
# json_data = json.dumps(json_data)

server.send_data_AES(message)

while True:
    message = server.receive_data_AES()
    
    if message is not None:
        with open('myfile.txt', 'w') as file:
            file.write(message)
