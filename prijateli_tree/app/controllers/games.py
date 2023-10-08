"""
Contains baseline structure for the game.
"""

# Global imports
import random


class Game:
    BAGS = ["Red", "Blue"]

    def __init__(self, players, max_rounds):
        self.players = players
        self.max_rounds = max_rounds
        self.current_round = 0
        self.network_structure = None
        # Bag compositions
        self.bags = {
            "red": ["red", "red", "red", "red", "blue", "blue"],
            "blue": ["blue", "blue", "blue", "blue", "red", "red"],
        }

    def setup_game(self):
        self.network_structure = self.decide_structure()
        self.bag = self.draw_bag()

    def decide_structure(self):
        if self.is_self_select():
            # Logic for self-selection
            pass
        else:
            # Randomize structure and player positions
            pass
        return structure

    def is_self_select(self):
        # Logic to decide self-select
        pass

    def draw_bag(self):
        """
        Randomly selects either a red or blue bag.
        """
        return random.choice(["red", "blue"])

    def distribute_balls(self):
        for player in self.players:
            ball = self.draw_ball_from_bag()
            player.observe(ball)  # Hypothetical method

    def draw_ball_from_bag(self):
        # Randomly draw a ball based on the bag's composition
        ball = random.choice(self.bags[self.bag])
        # Remove the drawn ball from the bag
        self.bags[self.bag].remove(ball)
        return ball

    def play_round(self):
        if self.current_round == 0:
            # First round logic: Players observe and make guesses
            pass
        else:
            # Players observe their ball and previous guesses of neighbors
            pass
        self.current_round += 1

    def play_game(self):
        self.setup_game()
        while self.current_round < self.max_rounds:
            self.play_round()
        self.end_game()

    def end_game(self):
        # Logic to inform players about the drawn bag and results
        pass
