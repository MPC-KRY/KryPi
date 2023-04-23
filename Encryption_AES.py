from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


""" 
Description: This function is used for Encrypting any string data with AES with CBC mode.
Parameters: str : message -> string data that will be encrypted
            bytes : key -> key that will be used for encryption
"""
def encrypt(message, key):
    # Convert the key and message to bytes
    message = message.encode('utf-8')

    # Pad the message to a multiple of 16 bytes
    padded_message = pad(message, AES.block_size)

    # Create a new AES cipher object with a random IV and the key
    iv = AES.new(key, AES.MODE_CBC).iv
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Encrypt the padded message
    encrypted_message = cipher.encrypt(padded_message)

    # Combine the IV and encrypted message, then convert to base64 and return as a string
    combined_message = iv + encrypted_message
    return base64.b64encode(combined_message).decode('utf-8')

""" 
Description: This function is used for Encrypting any bytes data with AES with CBC mode.
Parameters: bytes : message -> bytes data that will be encrypted
            bytes : key -> key that will be used for encryption
"""
def encrypt2(message, key):

    # Pad the message to a multiple of 16 bytes
    padded_message = pad(message, AES.block_size)

    # Create a new AES cipher object with a random IV and the key
    iv = AES.new(key, AES.MODE_CBC).iv
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Encrypt the padded message
    encrypted_message = cipher.encrypt(padded_message)

    # Combine the IV and encrypted message, then convert to base64 and return as a string
    combined_message = iv + encrypted_message

    return base64.b64encode(combined_message)


""" 
Description: This function is used for Decrypting any string data with AES with CBC mode.
Parameters: bytes : encrypted_message -> bytes data that will be decrypted
            bytes : key -> key that will be used for encryption
Returns: bytes : unpadded_message -> decrypted message in string
"""
def decrypt(encrypted_message, key):
    # Convert the key and encrypted message to bytes
    encrypted_message = base64.b64decode(encrypted_message)

    # Extract the IV and encrypted message, then create a new AES cipher object with them and the key
    iv = encrypted_message[:AES.block_size]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the message and unpad it
    decrypted_message = cipher.decrypt(encrypted_message[AES.block_size:])
    unpadded_message = unpad(decrypted_message, AES.block_size)

    # Convert the decrypted message to a string and return it
    return unpadded_message.decode('utf-8')

""" 
Description: This function is used for Decrypting any bytes data with AES with CBC mode.
Parameters: bytes : message -> bytes data that will be encrypted
            bytes : key -> key that will be used for encryption
Returns: bytes : unpadded_message -> decrypted message in bytes
"""
def decrypt2(encrypted_message, key):
    # Convert the key and encrypted message to bytes
    encrypted_message = base64.b64decode(encrypted_message)

    # Extract the IV and encrypted message, then create a new AES cipher object with them and the key
    iv = encrypted_message[:AES.block_size]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the message and unpad it
    decrypted_message = cipher.decrypt(encrypted_message[AES.block_size:])
    unpadded_message = unpad(decrypted_message, AES.block_size)

    return unpadded_message


