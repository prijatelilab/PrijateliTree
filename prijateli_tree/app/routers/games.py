import random
from collections import Counter
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from prijateli_tree.app.database import Game, GameAnswer, GameType, Player, SessionLocal
from prijateli_tree.app.utils.constants import BALL_BLUE, BALL_RED, WINNING_SCORE
from prijateli_tree.app.utils.games import Game as GameUtil


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def get_current_round(game_id: int, db: Session = Depends(get_db)):
    """
    Gets the game's current round given the game id
    """
    total_players = db.query(Player).filter_by(game_id=game_id).count()
    total_answers = db.query(GameAnswer).filter_by(game_id=game_id).count()
    current_round = total_answers // total_players + 1

    return current_round


@router.get("/{game_id}")
def route_game_access(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="game not found")
    return {"game_id": game_id}


@router.get("/{game_id}/player/{player_id}")
def route_game_player_access(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="game not found")

    if len([player for player in game.players if player.user_id == player_id]) != 1:
        raise HTTPException(
            status_code=HTTPStatus.NO_CONTENT, detail="player not found in game"
        )


@router.post("/{game_id}/player/{player_id}/answer")
def route_add_answer(
    game_id: int,
    player_id: int,
    player_answer: str,
    db: Depends(get_db),
    current_round: int,
):
    """
    Function that updates the player's guess in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="game not found")

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


def get_previous_answers(game_id: int, player_id: int, game_type: str, db: Session):
    """
    Function that returns the player's previous answer
    from the last round, along with the answers of their neighbors
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="game not found")

    # Get current round
    current_round = get_current_round(game_id, db)

    if current_round == 1:
        raise HTTPException(
            status_code=HTTPStatus.NO_CONTENT, detail="No previous answers"
        )
    else:
        last_round = current_round - 1

    # Get the player's previous answer
    player_answer = (
        db.query(GameAnswer)
        .filter_by(game_id=game_id, player_id=player_id, round=last_round)
        .one_or_none()
    )

    # Get the player's neighbors
    player = (
        db.query(Player).filter_by(game_id=game_id, user_id=player_id).one_or_none()
    )

    # Use game utils to get the player's neighbors
    game_util = GameUtil(game_type)
    neighbors = game_util.neighbors[player.position]

    # Get the neighbors' previous answers
    neighbor_1_answer_obj = (
        db.query(GameAnswer)
        .filter_by(game_id=game_id, round=last_round, position=neighbors[0])
        .one_or_none()
    )

    neighbor_2_answer_obj = (
        db.query(GameAnswer)
        .filter_by(game_id=game_id, round=last_round, position=neighbors[1])
        .one_or_none()
    )

    return {
        "your_previous_answer": player_answer.player_answer,
        "neighbor_1_previous_answer": neighbor_1_answer_obj.player_answer,
        "neighbor_2_previous_answer": neighbor_2_answer_obj.player_answer,
    }


@router.get("/{game_id}/player/{player_id}/round")
def view_round(game_id: int, player_id: int, db: Session = Depends(get_db)):
    """
    Function that returns the current round
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="game not found")

    # Get current round
    current_round = get_current_round(game_id, db)

    # Get game type data
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    if not game_type:
        raise HTTPException(
            status_code=HTTPStatus.NO_CONTENT, detail="Game type not found"
        )

    bag = game_type.bag

    if current_round == 1:
        # Pick a random letter from the bag and show it to the player
        ball = random.choice(bag)
        return {"round": current_round, "ball": ball}
    else:
        # Show the player their previous answer and the answers of their neighbors
        previous_answers = get_previous_answers(game_id, player_id, db)
        return {"round": current_round, "previous_answers": previous_answers}


@router.post("/{game_id}/player/{player_id}/score")
def route_add_score(
    game_id: int,
    player_id: int,
    player_answer: str,
    db: Depends(get_db),
):
    """
    Function that updates the player's score in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="game not found")

    # Find out the correct answer
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    bag = game_type.bag

    # Check if bag is red or blue
    correct_answer = get_bag_color(bag)

    # Get the player's previous answer
    latest_answers = get_previous_answers(game_id, player_id, db)
    player_answer = latest_answers["your_previous_answer"]

    if player_answer == correct_answer:
        # Create a new DENIR object
        # TODO - Calculate DENIR based on score and update
        return {"status": f"Congratulations! You won, your score is {WINNING_SCORE}"}

    else:
        # Create a new DENIR object
        # Update with 0 denirs
        return {
            "status": f"Better luck next time! Your score would've been {WINNING_SCORE}"
        }


@router.post("/{game_id}/player/{player_id}/integrated")
def integrated_game(game_id: int, player_id: int, db: Session = Depends(get_db)):
    """
    Logic for handling the integrated game
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")
    # Check if the player is in the game
    existing_player = (
        db.query(Player).filter_by(game_id=game_id, user_id=player_id).one_or_none()
    )
    if not existing_player:
        raise HTTPException(
            status_code=HTTPStatus.NO_CONTENT, detail="player is not in the game"
        )

    # Get current round
    current_round = get_current_round(game_id, db)

    if current_round > game.rounds:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT, detail="Game is over")

    if current_round < game.rounds:
        view_round(game_id, player_id, db)
        # Update the player's answer if they want to - HOW?!
        route_add_answer(game_id, player_id, "", db, current_round)
    else:
        # Final round
        view_round(game_id, player_id, db)
        # Update the player's answer if they want to - HOW?!
        route_add_answer(game_id, player_id, "", db, current_round)
        # Calculate the score
        route_add_score(game_id, player_id, "", db, current_round)
