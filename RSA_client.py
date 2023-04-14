from ecdsa import VerifyingKey
from Crypto.PublicKey import RSA
import os
import struct


def client_RSA():
    rsa_public_key = RSA.importKey(key)
    return rsa_public_key.encrypt(data, 32)[0]  # TODO documentation says it's not save to use this RSA encrypt


