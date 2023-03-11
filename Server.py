import socket
import threading

class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
        self.receive_thread = None

    
    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"server is listening on {self.host}:{self.port}")
              
        while True:
            self.conn, addr = self.sock.accept()
            print(f"Connected to {addr[0]}:{addr[1]}")
            
            self.receive_thread = threading.Thread(target=self.receive)
            self.receive_thread.start()
            

            
    def receive(self):     
        while True:
            data = self.receive_data()
            if not data:
                break
            print(f"Received message from client: {data}")
            self.send_data(data.upper())


    def send_data(self, data):
        if self.conn is not None:
            self.conn.send(data.encode())
            
            
    def receive_data(self):
        if self.conn is not None:
            data = self.conn.recv(1024).decode()
            return data
        
    def close(self):
        self.sock.close()
        
        
        
server = Server()
server.listen()
message = server.recieve_data()
print(message)

server.send_data("Hello_world")

while True:
    message = input("Enter a message to send to the server: ")
    server.send_data(message)   



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
        