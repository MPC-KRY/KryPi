from ecdsa import SigningKey, NIST384p, VerifyingKey
from sys import exit
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from getpass import getpass
import struct
import os

HELP_MESSAGE = """
    Certificate Authority tool
    This is tool for signing files data
        First you must generate public and private key with --generate and than
        you can sing files with 
    Options:

        --generate                              -generate or regenerate signature
        --sign <file_name> [output_file]         -sign file and save in [output_file] (optional) default is hash.sig
        --verify <file_name> [signature_file]    -verify signature [signature_file] (optional) default is hash.sig
        --help (-h)                             -show this help
"""

OPTIONS = ["--generate", "--sign", "--verify", "-h", "--help"]


def encrypt(key, source):
    key = SHA256.new(key).digest()
    IV = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    source = struct.pack("i", len(source)) + source  # add length
    padding = b"0" * (16 - len(source) % 16)
    return IV + encryptor.encrypt(source + padding)  # encrypt with padding


def decrypt(key, source):
    key = SHA256.new(key).digest()
    IV, source = source[:16], source[16:]
    decrypter = AES.new(key, AES.MODE_CBC, IV)
    source = decrypter.decrypt(source)  # decrypted data
    length = struct.unpack("i", source[:struct.calcsize("i")])[0]  # extract of length
    return source[struct.calcsize("i"): length + struct.calcsize("i")]  # ignore padding


# TODO Encrypt private key based on password
def generate_to_file(public_key_path: str = 'public_key.pem', private_key_path: str = 'private_key.pem',
                     password: bytes = b"password"):
    """
    Generates public, private key pairs for DSA
    """
    sk = SigningKey.generate(curve=NIST384p)  # uses NIST192p
    vk = sk.verifying_key
    with open(public_key_path, 'wb') as public_key:
        public_key.write(vk.to_pem())
    with open(private_key_path, 'wb') as private_key:
        private_key.write(encrypt(password, sk.to_pem()))


def sign_file(data_file: str, private_key_path: str = 'private_key.pem', hash_path: str = "hash.sig",
              password: bytes = b"password"):
    """
    Sing file with private key
    :param data_file: data to be signed
    :param hash_path: path where signature will be stored
    :param password: password for encryption
    """
    with open(data_file, 'rb') as data:
        with open(private_key_path, 'rb') as private_key:
            with open(hash_path, 'wb') as signature_file:
                sig = SigningKey.from_pem(decrypt(password, private_key.read())).sign(data.read())
                signature_file.write(sig)


def verify_signature(data_file: str, public_key_file: str = 'public_key.pem', hash_path: str = 'hash.sig'):
    """
    Verify signature with public key
    :param data_file: data to verification
    :param hash_path: signature path
    :return: True if verified successfully
    """
    with open(data_file, 'rb') as data:
        with open(public_key_file, 'rb') as public_key:
            with open(hash_path, 'rb') as signature:
                return VerifyingKey.from_pem(public_key.read()).verify(signature.read(), data.read())


def main(args: list):
    """
    GUI for generating, signing, and verification
    :param args: list of arguments (string)
    """
    from sys import exit

    isValidOpt = False
    for arg in args:
        if arg in OPTIONS:
            isValidOpt = True

    if not isValidOpt:
        print(HELP_MESSAGE)
        exit(1)

    for arg in args:
        if arg in ["-h", "--help"]:
            print(HELP_MESSAGE)
            exit(0)

    if "--generate" in args:
        password = getpass("Enter password for encryption: ").encode()
        try:
            if password == "":
                generate_to_file()
            else:
                generate_to_file(password=password)
        except Exception as e:
            print("Cannot open file")
            exit(1)

    if "--sign" in args:
        try:
            password = getpass("Enter password for encryption: ").encode()
            if password == "":
                if args.index("--sign") + 2 < len(args) and args[args.index("--sign") + 2] not in OPTIONS:
                    sign_file(args[args.index("--sign") + 1], hash_path=args[args.index("--sign") + 2])
                else:
                    sign_file(args[args.index("--sign") + 1])
            else:
                if args.index("--sign") + 2 < len(args) and args[args.index("--sign") + 2] not in OPTIONS:
                    sign_file(args[args.index("--sign") + 1], hash_path=args[args.index("--sign") + 2],
                              password=password)
                else:
                    sign_file(args[args.index("--sign") + 1], password=password)
        except Exception as e:
            print(e)
            print("The usage of --sign is --sign <filename> [output file]")
            exit(1)

    if "--verify" in args:
        try:
            if args.index("--verify") + 2 < len(args) and args[args.index("--verify") + 2] not in OPTIONS:
                valid = verify_signature(args[args.index("--verify") + 1], hash_path=args[args.index("--verify") + 2])
            else:
                valid = verify_signature(args[args.index("--verify") + 1])
            print("Successfully verified" if valid else "Verification failed")
        except Exception as e:
            print(e)
            print("The usage of --verify is --verify <filename> [signature file]")
            exit(1)


if __name__ == "__main__":
    import sys

    sys.argv = ["asd", "--generate", "--sign", "public_key_RSA.pem", "--verify", "public_key_RSA.pem"]
    main(sys.argv[1:])