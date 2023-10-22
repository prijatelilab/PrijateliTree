"""
Contains baseline structure for all three game types.
"""
from prijateli_tree.app.database import Game


def integrated_game(game: Game, game_id: int, player_id: int):
    """
    Function that handles the logic for integrated games.
    """
    pass


def segregated_game(game: Game, player_id: int):
    return {"game_id": game.id, "player_id": player_id}


def self_selected_game(game: Game, player_id: int):
    return {"game_id": game.id, "player_id": player_id}
