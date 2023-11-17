"""Script to test the games API endpoints."""

import requests


API = "http://localhost:8000/"

# Add answer


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
    print(api)
    response = requests.get(api)
    print(response.status_code)
    print(response.json())


# MAIN

if __name__ == "__main__":
    # Some tests
    test_get_player(1, 2)
    test_add_answer(1, 2, 1, "B")
