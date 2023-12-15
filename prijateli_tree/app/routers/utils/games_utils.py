from collections import Counter
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from prijateli_tree.app.database import (
    Game,
    GamePlayer,
    GameSessionPlayer,
    get_db,
)
from prijateli_tree.app.utils.constants import BALL_BLUE, BALL_RED
from prijateli_tree.app.utils.games import Game as GameUtil


def raise_exception_if_none(x, detail):
    if x is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)


def raise_exception_if_not(x, detail):
    if not x:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)


def get_bag_color(bag):
    """
    Gets color of the bag based on the number of red and blue balls
    """
    # Check if bag is red or blue
    balls_counter = Counter(bag)
    correct_answer = False
    if balls_counter[BALL_RED] > balls_counter[BALL_BLUE]:
        correct_answer = BALL_RED
    elif balls_counter[BALL_RED] < balls_counter[BALL_BLUE]:
        correct_answer = BALL_BLUE

    return correct_answer


def get_current_round(game_id: int, db: Session = Depends(get_db)) -> int:
    """
    Gets the game's current round given the game id
    """
    players = db.query(GamePlayer).filter_by(game_id=game_id).all()
    n_answers = 0

    for player in players:
        n_answers += len(player.answers)

    current_round = n_answers // len(players) + 1

    return current_round


def get_game_and_player(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    """
    Helper function to ensure game and player exist
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()

    raise_exception_if_none(game, detail="game not found")

    filtered_player = [p for p in game.players if p.id == player_id]

    raise_exception_if_not(len(filtered_player), detail="player not in game")

    return game, filtered_player[0]


def get_lang_from_player_id(player_id: int, db: Depends(get_db)):
    """
    Get language from player_id
    """
    player = db.query(GamePlayer).filter_by(id=player_id).one_or_none()

    raise_exception_if_none(player, detail="player not found")

    return player.language.abbr


def did_player_win(
    game: Game,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Helper function that determines if the player won,
    the color of the bag and their guess
    """

    # Check if bag is red or blue
    correct_color = get_bag_color(game.game_type.bag)

    # Get the player's previous answer
    latest_guess = get_previous_answers(game.id, player_id, db)
    player_guess = latest_guess["your_previous_answer"]

    return {
        "correct_color": correct_color,
        "player_guess": player_guess,
        "is_correct": player_guess == correct_color,
    }


def get_session_player_from_player(
    player: GamePlayer, db: Session = Depends(get_db)
):
    session_player = (
        db.query(GameSessionPlayer)
        .filter_by(id=player.session_player_id)
        .one_or_none()
    )

    raise_exception_if_none(
        session_player, detail="GameSessionPlayer not found"
    )

    return session_player


def get_previous_answers(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that returns the player's previous answer
    from the last round, along with the answers of their neighbors
    """
    game, player = get_game_and_player(game_id, player_id, db)

    # Get current round
    current_round = get_current_round(game_id, db)

    raise_exception_if_not(current_round > 1, detail="no previous answers")

    last_round = current_round - 1

    player_answer = [a for a in player.answers if a.round == last_round][0]

    # Use game utils to get the player's neighbors
    game_util = GameUtil(game.game_type.network)
    neighbors_positions = game_util.neighbors[player.position]

    neighbors_answers = []
    neighbors_names = []
    # Get the neighbors' previous answers
    for neighbor_position in neighbors_positions:
        this_neighbor = (
            db.query(GamePlayer)
            .filter_by(game_id=game_id, position=neighbor_position)
            .one_or_none()
        )
        this_answer = [
            a for a in this_neighbor.answers if a.round == last_round
        ][0]

        # Check if names are hidden
        if game.game_type.names_hidden:
            player_id = this_neighbor.user.id
            complete_name = f"Player {player.position}: "
        else:
            complete_name = f"{this_neighbor.user.first_name} {this_neighbor.user.last_name}: "

        neighbors_names.append(complete_name)
        neighbors_answers.append(this_answer.player_answer)

    return {
        "your_previous_answer": player_answer.player_answer,
        "neighbors_previous_answer": neighbors_answers,
        "neighbors_names": neighbors_names,
    }


def get_game_and_type(game_id: int, db: Session = Depends(get_db)):
    """
    Helper function to ensure game and game type exist
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()

    raise_exception_if_none(game, detail="game not found")

    return game, game.game_type


def get_score_and_name(player: GamePlayer, db: Session = Depends(get_db)):
    """
    Gets the player's score and name from the session player object
    by using the game player object
    """
    session_player = get_session_player_from_player(player, db)
    player_name = f"{player.user.first_name} {player.user.last_name}"
    player_score = session_player.points

    return player_name, player_score
