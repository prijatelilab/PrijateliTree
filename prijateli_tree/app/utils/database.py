"""Utility class and functions to store and retrieve data from the database."""
import psycopg2
from datetime import datetime

# Local imports
from keys import DB_CREDS


class DatabaseHandler:
    """Class to handle database connections."""

    def __init__(self):
        self.connection = psycopg2.connect(
            user=DB_CREDS["username"],
            password=DB_CREDS["password"],
            database=DB_CREDS["database"],
            host=DB_CREDS["host"],
            port=DB_CREDS["port"],
        )

    def create_game(self, game_id, user_id, game_type, rounds, practice):
        """
        Function used to create and handle game
        states and data.
        """
        cursor = self.connection.cursor()
        created_at = datetime.now()
        QUERY = f"""
            INSERT INTO games (id, created_at, created_by, game_type_id, rounds,
            practice)
            VALUES ({game_id}, '{created_at}', {user_id}, {game_type}, 
            {rounds}, {practice});
        """

        cursor.execute(QUERY)
        self.connection.commit()
        print(f"Game {game_id} created successfully in PostgreSQL")

    def add_player_to_game(self, player_id, game_id, user_id, position, name_hidden):
        """
        Function used to add a player to a game.
        """

        cursor = self.connection.cursor()
        QUERY = f"""
            INSERT INTO game_players (id, created_at, created_by, game_id, user_id,
            position, name_hidden)
            VALUES ({player_id}, '{datetime.now()}', {user_id}, {game_id}, {user_id},
            {position}, {name_hidden});
        """

        cursor.execute(QUERY)
        self.connection.commit()
        print(f"Player {player_id} added to game {game_id} successfully in PostgreSQL")
