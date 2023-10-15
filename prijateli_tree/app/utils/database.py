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
        QUERY = """
            INSERT INTO games (id, created_at, created_by, game_type_id, rounds,
            practice) VALUES (%s, %s, %s, %s, %s, %s);
        """
        try:
            cursor.execute(
                QUERY, (game_id, created_at, user_id, game_type, rounds, practice)
            )
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()  # Rollback any changes if an error occurred
            print(f"Error while creating game {game_id}: {e}")

        finally:
            cursor.close()

        print(f"Game {game_id} created successfully in PostgreSQL")

    def add_player_to_game(self, player_id, game_id, user_id, position, name_hidden):
        """
        Function used to add a player to a game.
        """

        cursor = self.connection.cursor()
        QUERY = """ INSERT INTO game_players (id, created_at, created_by, game_id, 
                user_id, position, name_hidden) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
        try:
            cursor.execute(
                QUERY,
                (player_id, datetime.now(), user_id, game_id, user_id, position, False),
            )
            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            print(f"Error while adding player {player_id} to game {game_id}: {e}")

        finally:
            cursor.close()

        print(f"Player {player_id} added to game {game_id} successfully in PostgreSQL")
