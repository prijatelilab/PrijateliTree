"""Script to test the games API endpoints."""

import requests


API = "http://localhost:8000/"

# Add answer


def test_add_answer(game_id, player_id, answer):
    """
    Adding answer for a given player.
    """
