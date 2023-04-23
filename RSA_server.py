from Crypto.PublicKey import RSA
from getpass import getpass

def count_RSA():
    RSA_LENGTH = 2048
    rsa_keys = RSA.generate(RSA_LENGTH)
    private_key = rsa_keys.exportKey()
    public_key = rsa_keys.publickey().exportKey()
    with open("public_key_RSA.pem", 'wb') as public_key_file:
        public_key_file.write(public_key)

    with open("private_key_RSA.pem", 'wb') as private_key_file:
        private_key_file.write(private_key)


if __name__ == '__main__':
    count_RSA()
    