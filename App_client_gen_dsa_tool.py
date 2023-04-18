import CA



def generate_DSA(username,password):
    CA.generate_to_file(f"public_key_DSA_{username}.pem",f"private_key_DSA_{username}.pem",password.encode())



username = input("input your acounts username: ")
password = input("input your acounts password: ")

generate_DSA(username,password)