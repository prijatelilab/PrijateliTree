import glob
import json
import random
from collections import Counter
from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from prijateli_tree.app.database import Game, GameAnswer, Player, SessionLocal
from prijateli_tree.app.utils.constants import (
    BALL_BLUE,
    BALL_RED,
    DENIR_FACTOR,
    FILE_MODE_READ,
    STANDARD_ENCODING,
    WINNING_SCORE,
)
from prijateli_tree.app.utils.games import Game as GameUtil


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))

languages = {}
for lang in glob.glob("prijateli_tree/app/languages/*.json"):
    with open(lang, FILE_MODE_READ, encoding=STANDARD_ENCODING) as file:
        languages.update(json.load(file))


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
    players = db.query(Player).filter_by(game_id=game_id).all()
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

    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    filtered_player = [p for p in game.players if p.id == player_id]

    if not len(filtered_player):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )
    return game, filtered_player[0]


def get_game_and_type(game_id: int, db: Session = Depends(get_db)):
    """
    Helper function to ensure game and game type exist
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()

    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    return game, game.game_type


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

    if current_round == 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No previous answers"
        )
    else:
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
            db.query(Player)
            .filter_by(game_id=game_id, position=neighbor_position)
            .one_or_none()
        )
        this_answer = [
            a for a in this_neighbor.answers if a.round == last_round
        ][0]
        complete_name = (
            f"{this_neighbor.user.first_name} {this_neighbor.user.last_name}: "
        )
        neighbors_names.append(complete_name)
        neighbors_answers.append(this_answer.player_answer)

    return {
        "your_previous_answer": player_answer.player_answer,
        "neighbors_previous_answer": neighbors_answers,
        "neighbors_names": neighbors_names,
    }


###############################
#
#        BEGIN API
#
###############################


@router.get("/{game_id}")
def route_game_access(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )
    return {
        "game_id": game_id,
        "rounds": game.rounds,
        "practice": game.practice,
    }


@router.get("/{game_id}/player/{player_id}")
def route_game_player_access(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    if len([player for player in game.players if player.id == player_id]) != 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not found in game"
        )

    return {"game_id": game_id, "player_id": player_id}


@router.post("/{game_id}/player/{player_id}/answer")
def route_add_answer(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
    body: dict = Body(...),
):
    """
    Function that updates the player's guess in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    correct_answer = get_bag_color(game.game_type.bag)

    # Extracting player_answer and current_round from the request body
    player_answer = body.get("player_answer")
    current_round = body.get("current_round")

    # Record the answer
    new_answer = GameAnswer(
        game_player_id=player_id,
        player_answer=player_answer,
        correct_answer=correct_answer,
        round=current_round,
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    return new_answer


@router.get("/{game_id}/player/{player_id}/round")
def view_round(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that returns the current round
    """
    game, player = get_game_and_player(game_id, player_id, db)
    # template_text = languages[player.language.abbr]
    current_round = get_current_round(game_id, db)
    # Get current round
    if current_round == 1:
        ball = random.choice(game.game_type.bag)
        first_round = True
        template_data = {
            "ball": ball,
            "first_round": first_round,
            "current_round": current_round,
        }
    else:
        previous_answers = get_previous_answers(game_id, player_id, db)
        first_round = False
        template_data = {
            "previous_answers": previous_answers,
            "first_round": first_round,
            "current_round": current_round,
        }

    return templates.TemplateResponse(
        "round.html", {"request": request, **template_data}
    )


@router.post("/{game_id}/player/{player_id}/update_score")
def route_add_score(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that updates the player's score in the database
    """

    # There isn't a place to store this right now as far as I can tell
    # player_session = ...

    # result = did_player_win(game_id, player_id, db)

    # we want to count the number of games they are correct, e.g.
    # player_session.n_correct += result["is_correct"]
    # player_session.total_points += result["is_correct"] * WINNING_SCORE
    url = "/{game_id}/player/{player_id}/end_of_game"

    return RedirectResponse(url=url, status_code=HTTPStatus.FOUND)


@router.get("/{game_id}/player/{player_id}/end_of_game")
def route_end_of_game(
    request: Request,
    game_id: int,
    player_id: int,
    debug: bool = False,
    db: Session = Depends(get_db),
):
    """
    Function that returns the end of game page and
    template.
    """

    game, player = get_game_and_player(game_id, player_id, db)
    game_status = did_player_win(game, player_id, db, debug)

    points = 0
    if game_status["is_correct"]:
        points = WINNING_SCORE

    template_text = languages[player.language.abbr]

    result = {
        "request": request,
        "player_id": player_id,
        "game_id": game_id,
        "points": points,
        "text": template_text,
    }

    # add information about winning and ball colors

    result.update(game_status)

    return templates.TemplateResponse("end_of_game.html", result)


@router.post("/{game_id}/player/{player_id}/denirs")
def score_to_denirs(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that calculates the denirs for the player
    given all of their scores
    """
    total_score = 0
    game, player = get_game_and_player(game_id, player_id, db)

    for answer in player.answers:
        if answer.player_answer == answer.correct_answer:
            total_score += WINNING_SCORE

    denirs = total_score * DENIR_FACTOR

    return {"reward": f"You have made {denirs} denirs!"}


@router.post("/player_ready")
def confirm_player(
    player_id: int,
    game_id: int,
    db: Session = Depends(get_db),
    body: dict = Body(...),
):
    """
    Confirms if the player is ready for the game
    """

    game, player = get_game_and_player(game_id, player_id, db)

    player.ready = True
    db.commit()

    return {"status": "Player is ready!"}
