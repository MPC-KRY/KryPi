import socket
import threading
import json



def key_data():
    
    data = Server.receive_data()


class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
    
    
    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"server is listening on {self.host}:{self.port}")
        self.conn, addr = self.sock.accept()

    def send_data(self, data):
        if self.conn is not None:
            self.conn.sendall(data.encode('utf-8'))
            print(data.encode('utf-8'))
            
    def receive_data(self):
        if self.conn is not None:
            data = self.conn.recv(1024).decode()
            return data
        
    def close(self):
        self.sock.close()
        

server = Server()
server.listen()



def read_json_data(file_path):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_data
json_data = read_json_data('JSON_data.json')
json_data = json.dumps(json_data)

server.send_data(json_data)

while True:
    message = server.receive_data()
    message = json.loads(message)
    if not message:
        break
    print(f'Received message from server: {message}')
    
print('finish')






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
        