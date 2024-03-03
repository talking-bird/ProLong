import hashlib
import os


def getRandomHash():
    # Generate a random string (you can use any method to generate a random string)
    random_string = os.urandom(16)

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the random string
    hash_object.update(random_string)

    # Get the hexadecimal representation of the hash
    random_hash = "0x" + hash_object.hexdigest()

    return random_hash
