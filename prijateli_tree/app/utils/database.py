"""Utility class and functions to store and retrieve data from the database."""
import psycopg2

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

    def fetch_game_by_id(self, game_id):
        """
        Function used to create and handle game
        states and data.
        """

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        cursor.close()
        return game
