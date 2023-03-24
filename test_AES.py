from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


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

def decrypt2(encrypted_message, key):
    # Convert the key and encrypted message to bytes
    encrypted_message = base64.b64decode(encrypted_message)

    # Extract the IV and encrypted message, then create a new AES cipher object with them and the key
    iv = encrypted_message[:AES.block_size]

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the message and unpad it
    decrypted_message = cipher.decrypt(encrypted_message[AES.block_size:])

    # Convert the decrypted message to a string and return it
    return decrypted_message.decode('utf-8')


