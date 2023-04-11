import socket
import tqdm
import os

# SEPARATOR = "<SEPARATOR>"
# BUFFER_SIZE = 4096 # send 4096 bytes each time step

# # the ip address or hostname of the server, the receiver
# host = "127.0.0.1"
# # the port, let's use 5001
# port = 5001
# # the name of file we want to send, make sure it exists
# filename = " vojta.1.1.jpg"
# # get the file size
# # print(os.path.realpath(filename))
# # filesize = os.path.getsize(filename)

# # # create the client socket
# # s = socket.socket()
# # print(f"[+] Connecting to {host}:{port}")
# # s.connect((host, port))
# # print("[+] Connected.")

# # # send the filename and filesize
# # s.send(f"{filename}{SEPARATOR}{filesize}".encode())

# # # start sending the file
# # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
# # with open(filename, "rb") as f:
# #     while True:
# #         # read the bytes from the file
# #         bytes_read = f.read(BUFFER_SIZE)
# #         if not bytes_read:
# #             # file transmitting is done
# #             break
# #         # we use sendall to assure transimission in 
# #         # busy networks
# #         s.sendall(bytes_read)
# #         # update the progress bar
# #         progress.update(len(bytes_read))
# # # close the socket
# # s.close()


# import socket

# class ImageSender:
#     def __init__(self):
#         self.host = "127.0.0.1"
#         self.port = 8080
#         self.SEPARATOR = "<SEPARATOR>"
#         self.BUFFER_SIZE = 4096
#         self.conn = None
#         self.sock = None
#         self.filesize = None
        
    
#     def listen(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.bind((self.host, self.port))
#         self.sock.listen()
#         print(f"server is listening on {self.host}:{self.port}")
#         self.conn, addr = self.sock.accept()


#     def sendImageData(self,filename):
#         filesize = os.path.getsize(filename)
#         self.sock.send(f"{filename}{self.SEPARATOR}{filesize}".encode())
#         return True


#     def send_image(self,filename):
#         # Create a TCP socket and connect to the server

#             progress = tqdm.tqdm(range(self.filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
#             with open(filename, "rb") as f:
#                 while True:
#                     # read the bytes from the file
#                     bytes_read = f.read(self.BUFFER_SIZE)
#                     if not bytes_read:
#                         # file transmitting is done
#                         break
#                     # we use sendall to assure transimission in 
#                     # busy networks
#                     self.sock.sendall(bytes_read)
#                     # update the progress bar
#                     progress.update(len(bytes_read))



# test.sendImageData(" vojta.1.1.jpg")
# test.send_image(" vojta.1.1.jpg")




import socket


class Client:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.sock = None
        self.json_data = None
        self.ECDH_key = None
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096
        self.filesize = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"connected to {self.host}:{self.port}")


    def close(self):
        self.sock.close()

        
    def send_data(self, data):
        if self.sock is not None:
            self.sock.send(data.encode('utf-8'))

    def receive_data(self):
        if self.sock is not None:
            data = self.sock.recv(1024)
            return data
        

    def sendImageData(self,filename):
        if self.sock is not None:
            self.filesize = os.path.getsize(filename)
            self.sock.send(f"{filename}{self.SEPARATOR}{self.filesize}".encode())


    def send_image(self,filename):
        # Create a TCP socket and connect to the server
        if self.sock is not None:
            progress = tqdm.tqdm(range(self.filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(filename, "rb") as f:
                while True:
                    print("something")
                    # read the bytes from the file
                    bytes_read = f.read(self.BUFFER_SIZE)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in 
                    # busy networks
                    self.sock.sendall(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))




res = []
def files():

# folder path
    dir_path = r'C:\\Users\\jakub\Documents\\GitHub\\KryPi\\test\\temp'

    # list to store files

    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            res.append(path)
    print(res)

if __name__ == '__main__':

    files()
    client = Client()
    client.connect()

    client.send_data("hello")
    for i in res:
        client.sendImageData(i)
        client.send_image(i)



            
        
