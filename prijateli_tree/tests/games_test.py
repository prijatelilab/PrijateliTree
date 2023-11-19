"""Script to test the games API endpoints."""
import random

import requests

from prijateli_tree.app.utils.constants import BALL_BLUE, BALL_RED


API = "http://localhost:8000/"
POSSIBLE_ANSWERS = [BALL_RED, BALL_BLUE]


def test_add_answer(game_id, player_id, round, answer):
    """
    Adding answer for a given player.
    """
    api = f"{API}games/{game_id}/player/{player_id}/answer"
    print(api)
    response = requests.post(
        api,
        json={
            "player_answer": answer,
            "current_round": round,
        },
    )
    print(response.status_code)
    print(response.json())


def test_get_player(game_id, player_id):
    """
    Getting player info.
    """
    api = f"{API}games/{game_id}/player/{player_id}"
    response = requests.get(api)
    print(response.status_code)
    print(response.json())


def test_view_round(game_id, player_id):
    """
    Getting round info.
    """
    api = f"{API}games/{game_id}/player/{player_id}/round"
    response = requests.get(api)
    print(response.status_code)
    print(response.json())


# MAIN

if __name__ == "__main__":
    # Some tests
    for player in range(1, 6):
        random_answer = random.choice(POSSIBLE_ANSWERS)
        test_add_answer(1, player, 1, random_answer)
    test_view_round(1, 3)
