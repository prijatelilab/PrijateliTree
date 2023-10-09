"""
Contains baseline structure for the game.
"""

# Global imports
import random
from random import shuffle

# Local imports
# from prijateli_tree.app.controllers.players import Player


class Game:
    def __init__(self, max_rounds, network_type, correct_points):
        self.players = []
        self.max_rounds = max_rounds
        self.current_round = 0
        self.network_type = network_type
        self.correct_points = correct_points
        # Bag compositions
        self.bags = {
            "red": ["red", "red", "red", "red", "blue", "blue"],
            "blue": ["blue", "blue", "blue", "blue", "red", "red"],
        }

        self.network_methods = {
            "integrated": self._create_integrated_network,
            "segregated": self._create_segregated_network,
            "self_select": self._create_self_select_network,
        }

    def assign_network(self, network_type):
        """
        Assigns a network structure to the game
        """
        if network_type not in self.network_methods:
            raise ValueError(f"Unknown network type: {network_type}")
        self.network = self.network_methods[network_type]()

    def _create_integrated_network(self):
        """
        Creates an integrated network, where players observe a player from their
        own nationality and from another
        """
        shuffle(self.players)
        network = {}

        # TO DO: Add logic to assign neighbors

        return network

    def _create_segregated_network(self):
        shuffle(self.players)
        network = {}

        # TO DO: Add logic to assign neighbors

        return network

    def _create_self_select_network(self):
        """
        Creates a self selected network where players choose their neighbors.
        """
        network = {}
        # TO DO: Add logic to assign neighbors
        return network

    def add_player(self, player):
        self.players.append(player)

    def setup_game(self):
        self.network_structure = self.decide_structure()
        self.bag = self.draw_bag()

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
            # First round logic: Players simply observe and make guesses
            for player in self.players:
                ball = self.draw_ball_from_bag()
                player.observe(ball)
                guess = player.make_guess()
                self.guesses[player.player_id] = guess
        else:
            # Players observe their ball and previous guesses of neighbors
            for player in self.players:
                ball = self.draw_ball_from_bag()
                player.observe(ball)
                neighbor_guesses = self.get_neighbor_guesses(player)
                player.observe_others_guesses(neighbor_guesses)
                updated_guess = (
                    player.update_guess()
                )  # Assuming players might change their guess
                self.guesses[player.player_id] = updated_guess

        self.current_round += 1

    def get_neighbor_guesses(self, player):
        """
        Returns a dictionary of player_id: guess pairs for the player's neighbors.
        """
        neighbor_guesses = {}
        for neighbor in self.network_structure[player.player_id]:
            neighbor_guesses[neighbor] = self.guesses[neighbor]
        return neighbor_guesses

    def calculate_points(self, player):
        """
        Calculates the points for a player based on their
        guess and the drawn bag.
        """
        player_guess = player.guess
        if player_guess == self.bag:
            print(f"Correct guess!, you will get {self.correct_points}")
            return self.correct_points
        else:
            print(
                "Better luck next time!, you would have gotten {self.correct_points} points"  # noqa: E501
            )
            return 0

    def end_game(self):
        """
        Calculates the points for each player and adds them to their score.
        """
        for player in self.players:
            points_won = self.calculate_points(player)
            player.add_points(points_won)

    def play_game(self):
        """
        Executes the game pipeline.
        """
        self.setup_game()
        while self.current_round < self.max_rounds:
            self.play_round()
        self.end_game()
