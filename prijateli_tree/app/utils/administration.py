"""Script for utils functions for the app's administration."""

from utils.constants import SHOW_NETWORK_PROBABILITY

import random


def show_network():
    """Return True if the network should be shown."""
    return random.random() < SHOW_NETWORK_PROBABILITY
