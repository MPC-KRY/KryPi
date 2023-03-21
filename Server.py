import socket
import threading

from Crypto.Cipher import AES
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import binascii

from cryptography.hazmat.primitives.serialization import load_der_public_key

import test_AES


class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
        self.receive_thread = None
        self.key = b"gQGP/E2SdzXvyhVoNmdoyvF66uBNZvuq"
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
            self.conn.send(data)

    def receive_data(self):
        if self.conn is not None:
            data = self.conn.recv(1024)
            return data

    def receive_data_AES(self):
        if self.conn is not None:
            data = self.conn.recv(1024)
            return test_AES.decrypt(data.decode(), self.ECDH_key)

    def close(self):
        self.sock.close()

    def countDH(self):

        #accepts the client's public key and creates its own private key
        Alice_public_key_bytes = self.receive_data()
        Bob_private_key = ec.generate_private_key(ec.SECP384R1())

        #converts the ECDH public key to bytes and sends it to the client
        Bob_public_key_bytes = Bob_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.send_data(Bob_public_key_bytes)

        #calculates the secret key
        Alice_public_key = load_der_public_key(Alice_public_key_bytes)
        size = 32
        Bob_shared_key = Bob_private_key.exchange(ec.ECDH(), Alice_public_key)
        Bob_derived_key = HKDF(hashes.SHA256(), size, None, b'', ).derive(Bob_shared_key)

        self.ECDH_key = binascii.b2a_hex(Bob_derived_key)[:32]
        print("\nBob's derived key: ", binascii.b2a_hex(Bob_derived_key).decode())





server = Server()
server.listen()
server.countDH()

print(server.receive_data_AES())





while True:
    message = input("Enter a message to send to the server: ")
    server.send_data_AES(message)

# HEADER = 64
# FORMAT = 'utf-8'
# HOST = '192.168.1.222'
# PORT =  9090
# DISCONECT = "disconect"

# #just for accepting conecitons
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind((HOST, PORT))

# # while True:
# #     comunication_socket, address = server.accept()
# #     print(f"Connecting to {address}")
# #     message = comunication_socket.recv(1024).decode('utf-8')
# #     print(f"mesage from client {message}")
# #     comunication_socket.send(f"Connecting to {address}, {message}, wowowowo".encode('utf-8'))
# #     comunication_socket.close()
# #     print("conection ended")


# def handle_client(conn, addr):
#     print(f"Connecting to {addr}")
#     connected = True
#     while connected:
#         msg_length = conn.recv(HEADER).decode(FORMAT)
#         if msg_length:
#             msg_length = int(msg_length)
#             msg = conn.recv(msg_length).decode(FORMAT)
#             if msg == DISCONECT:
#                 connected = False
#             print(f"[{addr}],{msg}")
#     conn.close()

#         # print(f"Connecting to {address}")
#         # message = comunication_socket.recv(1024).decode('utf-8')
#         # print(f"mesage from client {message}")
#         # comunication_socket.send(f"Connecting to {address}, {message}, wowowowo".encode('utf-8'))
#         # comunication_socket.close()
#         # print("conection ended")

#     pass
# def start():

#     server.listen()
#     print(f"listening on {HOST}")
#     while True:
#         comunication_socket, address = server.accept()
#         thread = threading.Thread(target=handle_client, args=(comunication_socket, address))
#         thread.start()
#         print(f"active connections: {threading.activeCount() -1}")

# print("server is starting ...")
# start()

# print(f"listening on {HOST}")
# while True:
# comunication_socket, address = server.accept()
# thread = threading.Thread(target=handle_client, args=(comunication_socket, address))
# thread.start()
# print(f"active connections: {threading.activeCount() -1}")
