
import random
import secrets
import string


def generate_strong_password(length: int = 16) -> str:
    if length < 4:
        raise ValueError("Password length must be at least 4 characters")

    # Required character sets
    lowercase = secrets.choice(string.ascii_lowercase)
    uppercase = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice(string.punctuation)

    # Remaining characters
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + string.punctuation
    remaining = [secrets.choice(all_chars) for _ in range(remaining_length)]

    # Combine all and shuffle
    password_list = list(lowercase + uppercase + digit + symbol) + remaining
    random.shuffle(password_list)

    return ''.join(password_list)