
import CA



def sign_DSA(username,password):
    CA.sign_file(f"public_key_DSA_{username}.pem",f"private_key_{username}.pem",f"hash_{username}_verify.sig",password.encode())
    



username = input("input your acounts username: ")
password = input("input your acounts password: ")

sign_DSA(username,password)