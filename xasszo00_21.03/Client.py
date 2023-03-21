import socket
import json
from Test import KryPiShell








#receive
#decipher
#format
##add 
    #generate pass
#delete
#edit
#show


class Client:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.sock = None
        self.json_data = None

        
    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"connected to {self.host}:{self.port}")
        
        
    def close(self):
        self.sock.close()
        
        
    def add_to_json_data(self,data):
        self.json_data = json.loads(data)
        
    def send_data(self,data):
        if self.sock is not None:
            self.sock.send(data.encode())
            
            
    def receive_data(self):
        if self.sock is not None:
            data = self.sock.recv(1024).decode()
            return data

        
            
           
if __name__ == '__main__':
    client = Client()
    client.connect()   
    json_data = client.receive_data()
    client.add_to_json_data(json_data)
    try:
        while True:
            krypi = KryPiShell()
            krypi.add_data(json_data)
            krypi.cmdloop()   
            data = krypi.retrieve_data()
            
            client.send_data(json.dumps(data)) 
            if input("Press"):
                break 
    except KeyboardInterrupt:
        data = krypi.retrieve_data() 
        client.send_data(json.dumps(data))
        print("Exiting....")


            
        
