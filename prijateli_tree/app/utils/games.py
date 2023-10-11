"""Utility functions for specific game types."""
from abc import ABC, abstractmethod

from prijateli_tree.app.utils.constants import NETWORK_TYPE_INTEGRATED, \
    NETWORK_TYPE_SEGREGATED, NETWORK_TYPE_SELF_SELECTED


class Game(ABC):
    @abstractmethod
    def is_neighboring_position(self, position: int, test_position: int):
        pass


class IntegratedGame(Game):
    def __init__(self):
        self.network_type = NETWORK_TYPE_INTEGRATED

    def is_neighboring_position(self, position: int, test_position: int):
        pass


class SegregatedGame(Game):
    def __init__(self):
        self.network_type = NETWORK_TYPE_SEGREGATED

    def is_neighboring_position(self, position: int, test_position: int):
        pass


class SelfSelectedGame(Game):
    def __init__(self):
        self.network_type = NETWORK_TYPE_SELF_SELECTED

    def is_neighboring_position(self, position: int, test_position: int):
        pass
