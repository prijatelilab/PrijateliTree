"""Script for utils functions for the app's administration."""

import random

from prijateli_tree.app.utils.constants import SHOW_NETWORK_PROBABILITY


def show_network():
    """Return True if the network should be shown."""
    return random.random() < SHOW_NETWORK_PROBABILITY
