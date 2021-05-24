import random
from itertools import cycle


def make_random_password(length=8):
    """
    Adds uppercase letters if there are no any, adds digits
    """
    stack = [
        'abcdefghijklmnopqrstuvwxyz',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        '0123456789',
    ]
    password_chars = []
    for i, char_set in zip(range(length), cycle(stack)):
        password_chars.append(random.choice(char_set))
    return ''.join(password_chars)
