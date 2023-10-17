"""
Contains baseline structure for all three game types.
"""
from prijateli_tree.app.database import Game
from prijateli_tree.app.utils.database import DatabaseHandler


def create_new_game(game_type, user_id, num_rounds, practice):
    """
    Uses the database handler to create a new game and return the game ID.
    """
    database = DatabaseHandler()
    game_id = database.get_next_game_id()
    # Insert the new game into the database
    database.create_game(game_id, user_id, game_type, num_rounds, practice)

    return game_id


def add_player_to_game(game_id, user_id, position, name_hidden=False):
    """
    Uses the database handler to add a player to a game and return the player ID.
    """
    database = DatabaseHandler()
    if not database.game_exists(game_id):
        raise ValueError(f"No game found with ID {game_id}")

    # Check if the user is already a player in the game
    if database.is_player_in_game(game_id, user_id):
        raise ValueError(f"User {user_id} is already a player in game {game_id}")

    # Logic to add the player
    player_id = database.get_next_player_id()

    database.add_player_to_game(player_id, game_id, user_id, position, name_hidden)

    return player_id


def integrated_game(game: Game, game_id: int, player_id: int):
    """
    Function that handles the logic for integrated games.
    """

    database = DatabaseHandler()

    # 1. Fetch the current game state and related data
    game_record = database.fetch_game_by_id(game_id)
    player_record = database.fetch_player_by_id(player_id)

    # Check if the game or player doesn't exist
    if not game_record or not player_record:
        raise ValueError("Game or player not found!")

    game = Game(
        id=game_record[0],
        created_at=game_record[1],
        created_by=game_record[2],
        game_type_id=game_record[3],
        rounds=game_record[4],
        practice=game_record[5],
    )

    return {"game_id": game.id, "player_id": player_id}


def segregated_game(game: Game, player_id: int):
    return {"game_id": game.id, "player_id": player_id}


def self_selected_game(game: Game, player_id: int):
    return {"game_id": game.id, "player_id": player_id}
