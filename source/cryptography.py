import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def generate_key_and_iv():
    return os.urandom(32), os.urandom(16)


def encrypt_data(file_data, key, iv):
    digest = hashes.Hash(hashes.SHA256())
    digest.update(file_data)
    data_hash = digest.finalize()

    padder = PKCS7(128).padder()
    padded_data = padder.update(file_data)
    padded_data += padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return encrypted_data, data_hash.hex()


def decrypt_data(path_to_file, key, iv):
    with open(path_to_file, "rb") as file:
        file_data = file.read()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    decrypted_data = decryptor.update(file_data) + decryptor.finalize()

    unpadder = PKCS7(128).unpadder()

    unpadded_data = unpadder.update(decrypted_data)
    unpadded_data += unpadder.finalize()

    return unpadded_data


def generate_public_and_private_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    return private_key, private_key.public_key()


def encrypt_data_via_public_key(public_key, data):
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def decrypt_data_via_private_key(private_key, data):
    return private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


"""
Utils
"""


def public_key2bytes(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


def private_key2bytes(private_key):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )


def bytes2public_key(public_key_bytes):
    return serialization.load_pem_public_key(b'-----BEGIN PUBLIC KEY-----' +
                                             public_key_bytes +
                                             b'-----END PUBLIC KEY-----')


def hex2private_key(private_key_hex):
    return serialization.load_pem_private_key(b'-----BEGIN PRIVATE KEY-----' +
                                              bytes.fromhex(private_key_hex[2:]) +
                                              b'-----END PRIVATE KEY-----')
