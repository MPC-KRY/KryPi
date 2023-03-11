import socket



class Client:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 8080
        self.sock = None

        
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"connected to {self.host}:{self.port}")
        
        
    def send_data(self,data):
        if self.sock is not None:
            self.sock.send(data.encode())
            
            
    def receive_data(self):
        if self.sock is not None:
            data = self.sock.recv(1024).decode()
            return data
        
    def close(self):
        self.sock.close()
        
            
           
           
client = Client()
client.connect()       



client.send_data("Hello_world")

message = client.receive_data()
print(message)

while True:
    message = input("Enter a message to send to the server: ")
    client.send_data(message)           
            


# HEADER = 64
# FORMAT = 'utf-8'
# HOST = '192.168.1.222'
# PORT =  9090
# DISCONECT = "disconect"


# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# client.connect((HOST, PORT))


# def send(msg):
#     message = msg.encode(FORMAT)
#     msg_len = len(message)
#     send_len = str(msg_len).encode(FORMAT)
    
    
    
    
    

# client.send(f"Hello world".encode("utf-8"))
# print(client.recv(1024))



