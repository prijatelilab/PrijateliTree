"""Script for utils functions for the app's administration."""

import random

from passlib.context import CryptContext

from prijateli_tree.app.utils.constants import SHOW_NETWORK_PROBABILITY


def show_network():
    """Return True if the network should be shown."""
    return random.random() < SHOW_NETWORK_PROBABILITY


# hat tip: https://www.fastapitutorial.com/blog/password-hashing-fastapi/
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
