"""Utility functions for specific game types."""

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
from prijateli_tree.app.utils.constants import (
    BALL_BLUE,
    BALL_RED,
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SEGREGATED,
    NETWORK_TYPE_SELF_SELECTED,
)


class GameUtil:
    def __init__(
        self,
        network_type=NETWORK_TYPE_INTEGRATED,
    ):
        self.network_type = network_type
        if network_type == NETWORK_TYPE_INTEGRATED:
            self.neighbors = {
                1: [3, 5],
                2: [3, 6],
                3: [1, 2, 4],
                4: [5, 3, 6],
                5: [1, 4],
                6: [4, 2],
            }
        elif network_type == NETWORK_TYPE_SEGREGATED:
            self.neighbors = {
                1: [2, 3],
                2: [1, 3],
                3: [1, 2, 4],
                4: [3, 5, 6],
                5: [4, 6],
                6: [4, 5],
            }
        elif network_type == NETWORK_TYPE_SELF_SELECTED:
            self.neighbors = {
                1: [],
                2: [],
                3: [],
                4: [],
                5: [],
                6: [],
            }

    def is_neighboring_position(self, position: int, test_position: int):
        if position in self.neighbors:
            return test_position in self.neighbors[position]

        return False


def raise_exception_if_none(x, detail) -> None:
    if x is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)


def raise_exception_if_not(x, detail) -> None:
    if not x:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)


def get_bag_color(bag) -> str:
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
) -> (Game, GamePlayer):
    """
    Helper function to ensure game and player exist
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()

    raise_exception_if_none(game, detail="game not found")

    filtered_player = [p for p in game.players if p.id == player_id]

    raise_exception_if_not(len(filtered_player), detail="player not in game")

    return game, filtered_player[0]


def get_lang_from_player_id(player_id: int, db: Depends(get_db)) -> str:
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
) -> dict:
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
) -> GameSessionPlayer | None:
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
) -> dict:
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
            complete_name = f"Player {this_neighbor.position}: "
        else:
            complete_name = f"{this_neighbor.user.first_name} {this_neighbor.user.last_name}: "

        neighbors_names.append(complete_name)
        neighbors_answers.append(this_answer.player_answer)

    return {
        "your_previous_answer": player_answer.player_answer,
        "neighbors_previous_answer": neighbors_answers,
        "neighbors_names": neighbors_names,
    }


def get_game_and_type(
    game_id: int, db: Session = Depends(get_db)
) -> (Game, str):
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

    return {"player_name": player_name, "player_score": player_score}


def get_header_data(player: GamePlayer, db: Session = Depends(get_db)):
    """
    Gets the player's score, name and game progress
    """
    score_dict = get_score_and_name(player, db)
    progress_dict = get_games_progress(player, db)

    return {**score_dict, **progress_dict}


def get_games_progress(player: GamePlayer, db: Session = Depends(get_db)):
    """
    Gets the player's progress in the overall session
    """
    session_player = get_session_player_from_player(player, db)
    session_id = session_player.session_id

    # Get practice and real game ids
    practice_games = (
        db.query(Game)
        .filter_by(game_session_id=session_id, practice=True)
        .order_by(Game.id)
        .all()
    )
    num_practice_games = len(practice_games)

    real_games = (
        db.query(Game)
        .filter_by(game_session_id=session_id, practice=False)
        .order_by(Game.id)
        .all()
    )
    num_real_games = len(real_games)

    # Select completed games by player
    completed_games = (
        db.query(GamePlayer)
        .filter_by(session_player_id=session_player.id, completed_game=True)
        .all()
    )

    # Get number of completed games
    completed_practice_games = 0
    completed_real_games = 0

    # List of ids of completed games
    completed_games_ids = [game.game_id for game in completed_games]

    for real_game in real_games:
        real_game_id = real_game.id
        if real_game_id in completed_games_ids:
            completed_real_games += 1

    for practice_game in practice_games:
        practice_game_id = practice_game.id
        if practice_game_id in completed_games_ids:
            completed_practice_games += 1

    current_practice_game = completed_practice_games + 1
    current_real_game = completed_real_games + 1

    # Ensure current game is not higher than the number of games
    if current_practice_game > num_practice_games:
        current_practice_game = num_practice_games

    if current_real_game > num_real_games:
        current_real_game = num_real_games

    practice_game_progress = f"{current_practice_game}/{num_practice_games}"
    real_game_progress = f"{current_real_game}/{num_real_games}"

    return {
        "practice_game_progress": practice_game_progress,
        "real_game_progress": real_game_progress,
    }
