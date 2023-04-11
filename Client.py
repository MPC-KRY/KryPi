import socket
import json
from Test import KryPiShell
from Client_ReadFace import FaceCapturer
import NetworkUtils

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import binascii

from cryptography.hazmat.primitives.serialization import load_der_public_key
import test_AES
import Client_DetectFace


class Client:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.sock = None
        self.json_data = None
        self.ECDH_key = None
        self.AES_key = b"696d8716547961c3ae99f8da734250c8"

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"connected to {self.host}:{self.port}")

        self.countDHEC()

    def close(self):
        self.sock.close()

    def add_to_json_data(self, data):
        self.json_data = json.loads(data)

    def send_data(self, data):
        if self.sock is not None:
            NetworkUtils.send_row(self.sock, data)

    def send_data_AES(self, data):
        if self.sock is not None:
            data = test_AES.encrypt(data, self.ECDH_key).encode()
            NetworkUtils.send_row(self.sock, data)


    def send_pictures_AES(self,data):
        if self.sock is not None:
            data = test_AES.encrypt2(data, self.ECDH_key)
            NetworkUtils.send_row(self.sock, data)

    def receive_data(self):
        if self.sock is not None:
            data = NetworkUtils.recv_row(self.sock)
            return data

    def receive_data_AES(self):
        if self.sock is not None:
            data = NetworkUtils.recv_row(self.sock)
            return test_AES.decrypt(data, self.ECDH_key)

    def countDHEC(self):

        # generate private key and converts the ECDH public key to bytes and sends it to the client
        Alice_private_key = ec.generate_private_key(ec.SECP384R1())
        Alice_public_key_bytes = Alice_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.send_data(Alice_public_key_bytes)

        # accepts the client's public key in bytes and convert it to public key object
        Bob_public_key_bytes = self.receive_data()
        Bob_public_key = load_der_public_key(Bob_public_key_bytes)

        # calculates the secret key
        size = 32
        Alice_shared_key = Alice_private_key.exchange(ec.ECDH(), Bob_public_key)
        Alice_derived_key = HKDF(hashes.SHA256(), size, None, b'', ).derive(Alice_shared_key)

        self.ECDH_key = binascii.b2a_hex(Alice_derived_key)[:32]
        print("\nBob's derived key: ", binascii.b2a_hex(Alice_derived_key).decode())

if __name__ == '__main__':
    client = Client()
    client.connect()

    json_data = client.receive_data_AES()
    json_data = test_AES.decrypt(json_data, client.AES_key)
    client.add_to_json_data(json_data)
    try:
        
        #send_picture_data()
        choice = input("choose")
        if choice == "1":   
            pass
        else:
            krypi = KryPiShell()
            krypi.add_data(json_data)
            krypi.cmdloop()
            data = krypi.retrieve_data()

            data = test_AES.encrypt(json.dumps(data), client.AES_key)
            client.send_data_AES(data)

    except KeyboardInterrupt:
        data = krypi.retrieve_data()
        client.send_data_AES(test_AES.encrypt(json.dumps(data), client.AES_key))
        print("Exiting....")



