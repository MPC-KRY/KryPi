import socket
import tqdm
import os
# device's IP address
# SERVER_HOST = "127.0.0.1"
# SERVER_PORT = 5001
# # receive 4096 bytes each time
# BUFFER_SIZE = 4096
# SEPARATOR = "<SEPARATOR>"

# # # create the server socket
# # # TCP socket
# # s = socket.socket()

# # # bind the socket to our local address
# # s.bind((SERVER_HOST, SERVER_PORT))

# # s.listen(5)
# # print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


# # client_socket, address = s.accept() 
# # # if below code is executed, that means the sender is connected
# # print(f"[+] {address} is connected.")



# # # receive the file infos
# # # receive using client socket, not server socket
# # received = client_socket.recv(BUFFER_SIZE).decode()
# # filename, filesize = received.split(SEPARATOR)
# # # remove absolute path if there is
# # filename = os.path.basename(filename)
# # # convert to integer
# # filesize = int(filesize)


# # # start receiving the file from the socket
# # # and writing to the file stream
# # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
# # with open(filename, "wb") as f:
# #     while True:
# #         # read 1024 bytes from the socket (receive)
# #         bytes_read = client_socket.recv(BUFFER_SIZE)
# #         if not bytes_read:    
# #             # nothing is received
# #             # file transmitting is done
# #             break
# #         # write to the file the bytes we just received
# #         f.write(bytes_read)
# #         # update the progress bar
# #         progress.update(len(bytes_read))

# # # close the client socket
# # client_socket.close()
# # # close the server socket
# # s.close()




# class ReceiveImage():
#     def __init__(self):
#         self.host = "127.0.0.1"
#         self.port = 8080
#         self.BUFFER_SIZE = 4096
#         self.SEPARATOR = "<SEPARATOR>"
#         self.filename = None
#         self.filesize = None
#         self.socket = None
#         self.conn = None

#     def receiveImageData(self):
#         received = self.socket.recv(self.BUFFER_SIZE).decode()
#         filenamee, filesizee = received.split(self.SEPARATOR)
#         self.filename = os.path.basename(filenamee)
#         self.filesize = int(filesizee)
#         return True
    
#     def receiveImage(self):
#         progress = tqdm.tqdm(range(self.filesize), f"Receiving {self.filename}", unit="B", unit_scale=True, unit_divisor=1024)
#         with open(self.filename, "wb") as f:
#             while True:
#                 # read 1024 bytes from the socket (receive)
#                 bytes_read = self.sock.recv(self.BUFFER_SIZE)
#                 if not bytes_read:    
#                     # nothing is received
#                     # file transmitting is done
#                     break
#                 # write to the file the bytes we just received
#                 f.write(bytes_read)
#                 # update the progress bar
#                 progress.update(len(bytes_read))


#     def listen(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.bind((self.host, self.port))
#         self.sock.listen()
#         print(f"server is listening on {self.host}:{self.port}")
#         self.conn, addr = self.sock.accept()



# server = ReceiveImage()

# server.listen()
# server.receiveImageData()
# server.receiveImage()




import socket



class Server:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.socket = None
        self.conn = None
        self.SEPARATOR = "<SEPARATOR>"
        self.BUFFER_SIZE = 4096

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen()
        print(f"server is listening on {self.host}:{self.port}")
        self.conn, addr = self.sock.accept()

    def send_data(self, data):
        if self.conn is not None:
            self.conn.send(data)

  
            
    def receive_data(self):
        if self.conn is not None:
            data = self.conn.recv(1024)
            return data

    def receiveImageData(self):
        if self.conn is not None:

            received = self.conn.recv(self.BUFFER_SIZE).decode()
            print(received.split("<SEPARATOR>"))
            filenamee, filesizee = received.split("<SEPARATOR>")
           # filesize = received.split("<SEPARATOR>")
            self.filename = os.path.basename(filenamee)
            self.filesize = int(filesizee)

        



    def receiveImage(self):
        if self.conn is not None:
            progress = tqdm.tqdm(range(self.filesize), f"Receiving {self.filename}", unit="B", unit_scale=True, unit_divisor=1024)
            print(self.filename)
            with open(self.filename, "wb") as f:
                print("here")
                while True:
                    # read 1024 bytes from the socket (receive)
                    bytes_read = self.conn.recv(self.BUFFER_SIZE)
                    if not bytes_read:    
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))
    
        
    def close(self):
        self.sock.close()


server = Server()
server.listen()
help = server.receive_data()
print(help)
while True:
    server.receiveImageData()
    server.receiveImage()



