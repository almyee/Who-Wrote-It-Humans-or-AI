# This script generates a secure random password.

import random
import string

def create_secure_password(password_length: int = 12) -> str:
    """
    Generates a secure password of a specified length.

    Args:
        password_length (int): The desired length of the password.

    Returns:
        str: A randomly generated password.
    """
    all_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(all_characters, k=password_length))

if __name__ == "__main__":
    print("Secure Password:", create_secure_password())

