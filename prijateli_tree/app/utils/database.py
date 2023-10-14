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

        now = datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")

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
