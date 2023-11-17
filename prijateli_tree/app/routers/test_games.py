"""Script to test the games API endpoints."""

import requests


API = "http://localhost:8000/"

# Add answer


def test_add_answer(game_id, player_id, answer):
    """
    Adding answer for a given player.
    """

    response = requests.post(
        f"{API}games/{game_id}/players/{player_id}/answer",
        json={"answer": answer},
    )
    print(response.status_code)
    print(response.json())


def test_get_player(game_id, player_id):
    """
    Getting player info.
    """

    response = requests.get(f"{API}games/{game_id}/players/{player_id}")
    print(response.status_code)
    print(response.json())


# MAIN

if __name__ == "__main__":
    # Some tests
    test_get_player(1, 2)
    test_add_answer(1, 2, "B")
