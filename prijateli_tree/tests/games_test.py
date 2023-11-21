"""Script to test the games API endpoints."""
import random
from http import HTTPStatus

import requests

from prijateli_tree.app.utils.constants import BALL_BLUE, BALL_RED


API = "http://localhost:8000/"
POSSIBLE_ANSWERS = [BALL_RED, BALL_BLUE]


def add_answer(game_id, player_id, round, answer):
    """
    Adding answer for a given player.
    """
    api = f"{API}games/{game_id}/player/{player_id}/answer"
    response = requests.post(
        api,
        json={
            "player_answer": answer,
            "current_round": round,
        },
    )

    return response.status_code


def test_add_answer():
    """
    Tests if the 'add answer' endpoint works.
    """
    response = test_add_answer()
    assert response(1, 2, 1, "R") == HTTPStatus.OK


def view_round(game_id, player_id):
    """
    Getting round info.
    """
    api = f"{API}games/{game_id}/player/{player_id}/round"
    response = requests.get(api)

    return response.status_code


def test_view_round():
    """
    Tests if the 'view round' endpoint works.
    """
    response = test_view_round()
    assert response(1, 2) == HTTPStatus.OK


# MAIN

if __name__ == "__main__":
    # Some tests
    for player in range(1, 6):
        random_answer = random.choice(POSSIBLE_ANSWERS)
        test_add_answer(1, player, 1, random_answer)
    test_view_round(1, 3)
