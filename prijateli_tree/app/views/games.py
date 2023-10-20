"""
Contains baseline structure for all three game types.
"""
from prijateli_tree.app.database import Game


def create_new_game(game_type, user_id, num_rounds, practice):
    """
    Uses the database handler to create a new game and return the game ID.
    """
    pass


def add_player_to_game(game_id, user_id, position, name_hidden=False):
    """
    Uses the database handler to add a player to a game and return the player ID.
    """
    pass


def integrated_game(game: Game, game_id: int, player_id: int):
    """
    Function that handles the logic for integrated games.
    """
    pass


def segregated_game(game: Game, player_id: int):
    return {"game_id": game.id, "player_id": player_id}


def self_selected_game(game: Game, player_id: int):
    return {"game_id": game.id, "player_id": player_id}
