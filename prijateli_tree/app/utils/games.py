"""Utility functions for specific game types."""

from prijateli_tree.app.utils.constants import (
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SEGREGATED,
    NETWORK_TYPE_SELF_SELECTED,
)


class Game:
    def __init__(self, network_type: str):
        self.network_type = network_type
        if network_type == NETWORK_TYPE_INTEGRATED:
            self.neighbors = {
                1: [3, 5],
                2: [3, 6],
                3: [1, 2, 4],
                4: [5, 3, 6],
                5: [1, 4],
                6: [4, 2],
            }
        elif network_type == NETWORK_TYPE_SEGREGATED:
            self.neighbors = {
                1: [2, 3],
                2: [1, 3],
                3: [1, 2, 4],
                4: [3, 5, 6],
                5: [4, 6],
                6: [4, 5],
            }
        elif network_type == NETWORK_TYPE_SELF_SELECTED:
            self.neighbors = {
                1: [],
                2: [],
                3: [],
                4: [],
                5: [],
                6: [],
            }

    def is_neighboring_position(self, position: int, test_position: int) -> bool:
        if position in self.neighbors:
            return test_position in self.neighbors[position]

        return False
