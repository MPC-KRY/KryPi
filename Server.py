import mysql.connector
import hashlib
import socket
import threading
import rsa

import pyotp
totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")

print("Current OTP:", totp.now())
public_key, private_key = rsa.newkeys(1024)
public_partner = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("192.168.0.227", 9992))

server.listen()




def handle_connection(c):
    
    client.send(public_key.save_pkcs1("PEM"))
    public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
    print(public_key)
    
    c.send(rsa.encrypt("Username".encode(), public_partner))
    
    print("test1")
    username = rsa.decrypt(c.recv(1024), private_key).decode()
    print("test2")

    c.send(rsa.encrypt("Password".encode(),public_partner))
    password = rsa.decrypt(c.recv(1024), private_key)
    password = hashlib.sha256(password).hexdigest()
    print("after first mesages")
    
    conn = mysql.connector.connect(
    host="localhost",
    user="jakub",
    password="password",
    database="mydatabase"
)
    
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM customers WHERE name = %s AND address = %s", (username, password))
    
    if cur.fetchall():
        c.send(rsa.encrypt("login successful".encode(),public_partner))
        c.send(rsa.encrypt("you got into the database great".encode(),public_partner))
        
        cur.execute("SELECT * FROM passwords")

        myresult = cur.fetchall()

        for x in myresult:
            #c.send(rsa.encrypt(x,public_partner))
            print(x)

    else:
        c.send("login failed".encode())    
        
        
        
while True:
    client, addr = server.accept()
    threading.Thread(target=handle_connection, args=(client,)).start()