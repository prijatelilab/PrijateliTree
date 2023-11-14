import glob
import json
import random
from collections import Counter
from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from prijateli_tree.app.database import (
    Game,
    GameAnswer,
    GameType,
    Player,
    SessionLocal,
    User,
)
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
for lang in glob.glob("../languages/*.json"):
    lang_code = lang.split("\\")[1].split(".")[0]

    with open(lang, FILE_MODE_READ, encoding=STANDARD_ENCODING) as file:
        languages[lang_code] = json.load(file)


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
    answers = []
    for player in players:
        answers.append(player.answers)
    current_round = len(answers) // len(players) + 1

    return current_round


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
    player_answer: str,
    current_round: int,
    db: Session = Depends(get_db),
):
    """
    Function that updates the player's guess in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

        # Get game type data
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()

    correct_answer = get_bag_color(game_type.bag)

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

    return {"status": "New answer recorded", "round": current_round}


def get_previous_answers(
    game_id: int,
    player_id: int,
    game_type: str,
    db: Session = Depends(get_db),
):
    """
    Function that returns the player's previous answer
    from the last round, along with the answers of their neighbors
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    # Get current round
    current_round = get_current_round(game_id, db)

    if current_round == 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No previous answers"
        )
    else:
        last_round = current_round - 1

    # Get the player's neighbors
    player = (
        db.query(Player)
        .filter_by(game_id=game_id, user_id=player_id)
        .one_or_none()
    )
    player_answer = [a for a in player.answers if a.round == last_round][0]

    # Use game utils to get the player's neighbors
    game_util = GameUtil(game_type)
    neighbors = game_util.neighbors[player.position]

    # Get the neighbors' previous answers
    neighbor_1 = (
        db.query(Player)
        .filter_by(game_id=game_id, round=last_round, position=neighbors[0])
        .one_or_none()
    )
    neighbor_1_answer = [
        a for a in neighbor_1.answers if a.round == last_round
    ][0]

    neighbor_2 = (
        db.query(Player)
        .filter_by(game_id=game_id, round=last_round, position=neighbors[1])
        .one_or_none()
    )
    neighbor_2_answer = [
        a for a in neighbor_2.answers if a.round == last_round
    ][0]

    return {
        "your_previous_answer": player_answer.player_answer,
        "neighbor_1_previous_answer": neighbor_1_answer.player_answer,
        "neighbor_2_previous_answer": neighbor_2_answer.player_answer,
    }


@router.get("/{game_id}/player/{player_id}/round")
def view_round(game_id: int, player_id: int, db: Session = Depends(get_db)):
    """
    Function that returns the current round
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    player = None
    for p in game.players:
        if p.id == player_id:
            player = db.query(User).filter_by(id=p.user_id).one_or_none()

    if player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )

    # Here's where you can get the correct text for your templating.
    # template_text = languages[player.language.abbr]

    # Get current round
    current_round = get_current_round(game_id, db)

    if current_round == 1:
        # Pick a random letter from the bag and show it to the player
        ball = random.choice(game.game_type.bag)
        return {"round": current_round, "ball": ball}
    else:
        # Show the player their previous answer and their neighbors
        previous_answers = get_previous_answers(game_id, player_id, db)
        return {"round": current_round, "previous_answers": previous_answers}


@router.post("/{game_id}/player/{player_id}/score")
def route_add_score(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that updates the player's score in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    player = None
    for p in game.players:
        if p.id == player_id:
            player = db.query(User).filter_by(id=p.user_id).one_or_none()

    if player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )

    # Here's where you can get the correct text for your templating.
    # template_text = languages[player.language.abbr]

    # Find out the correct answer
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    bag = game_type.bag

    # Check if bag is red or blue
    correct_answer = get_bag_color(bag)

    # Get the player's previous answer
    latest_answers = get_previous_answers(game_id, player_id, db)
    player_answer = latest_answers["your_previous_answer"]

    if player_answer == correct_answer:
        # Update the player's score
        return {
            "status": "Correct!",
            "score": f"{WINNING_SCORE} points have been added to your score",
        }
    else:
        # Update the player's score
        return {
            "status": "Better luck next time!",
            "score": f"Your score would've won {WINNING_SCORE}",
        }


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
    player = (
        db.query(Player)
        .filter_by(user_id=player_id, game_id=game_id)
        .one_or_none()
    )
    if player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )

    for answer in player.answers:
        if answer.player_answer == answer.correct_answer:
            total_score += WINNING_SCORE

    denirs = total_score * DENIR_FACTOR

    return {"reward": f"You have made {denirs} denirs!"}


@router.post("/{game_id}/player/{player_id}/integrated")
def integrated_game(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    """
    Logic for handling the integrated game
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    # TODO: We need to go over this one
    existing_player = (
        db.query(Player).filter_by(game_id=game_id, id=player_id).one_or_none()
    )
    if not existing_player:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )
    # Get current round
    current_round = get_current_round(game_id, db)

    if current_round > game.rounds:
        return {"message": "Game over"}

    view_round(game_id, player_id, db)
    # Update the player's answer if they want to - HOW?!
    route_add_answer(game_id, player_id, "", current_round, db)
    # Calculate the score
    route_add_score(game_id, player_id, db)
    if current_round == game.rounds:
        # Final round - calculate the denirs
        score_to_denirs(game_id, player_id, db, current_round)


@router.post("/ready")
def confirm_player(
    player_id: int,
    game_id: int,
    db: Session = Depends(get_db),
):
    """
    Confirms if the player is ready for the game
    """

    player = db.query(Player).filter_by(id=player_id, game_id=game_id)
    if player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )

    player.ready = True
    db.commit()

    return {"status": "Player is ready!"}
