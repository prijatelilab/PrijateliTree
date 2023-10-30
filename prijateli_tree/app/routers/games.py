import random
from collections import Counter
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from prijateli_tree.app.database import Game, GameAnswer, GameType, Player, SessionLocal
from prijateli_tree.app.schemas import GameCreate, PlayerCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/")
def route_create_game(
    game_data: GameCreate,
    db: Session = Depends(get_db),
):
    return {"status": "success"}


@router.post("/game/{game_id}/player/")
def route_add_player(
    game_id: int, player_data: PlayerCreate, db: Session = Depends(get_db)
):
    return {"status": "success"}


@router.get("/{game_id}")
def route_game_access(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")
    return {"game_id": game_id}


@router.get("/{game_id}/player/{player_id}")
def route_game_player_access(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")

    if len([player for player in game.players if player.user_id == player_id]) != 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not found in game"
        )


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
        raise HTTPException(status_code=400, detail="Player is not in the game")

    # Get game type data
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    bag = game_type.bag

    # Check if bag is red or blue
    balls_counter = Counter(bag)
    if balls_counter["R"] > balls_counter["B"]:
        bag_color = "R"
    elif balls_counter["R"] < balls_counter["B"]:
        bag_color = "B"

    if not game_type:
        raise HTTPException(status_code=400, detail="Game type not found")

    # Get current round
    total_players = db.query(Player).filter_by(game_id=game_id).count()
    total_answers = db.query(GameAnswer).filter_by(game_id=game_id).count()
    current_round = total_answers // total_players + 1

    if current_round > game.rounds:
        raise HTTPException(status_code=400, detail="Game is over")

    if current_round == 1:
        # Pick a random letter from the bag and show it to the player
        ball = random.choice(bag)
        return {
            "message": f"It's the first round! Here's the ball: {ball}. Make your guess now!",
            "ball": ball,
            "round": current_round,
        }

        # Record the player's answer

    else:
        # Show the player the previous round's answer
        # Show the neighbor's answers from the previous round
        # Update the player's answer if they want to
        pass


@router.get("/round-progress/{game_id}/{current_round}")
def check_round_progress(
    game_id: int, current_round: int, db: Session = Depends(get_db)
):
    total_players = db.query(Player).filter_by(game_id=game_id).count()
    players_answered = (
        db.query(GameAnswer).filter_by(game_id=game_id, round=current_round).count()
    )

    # Check if all players have provided their answers
    if players_answered == total_players:
        return {
            "status": "ready_for_next_round",
            "message": "All players have answered! Proceeding to the next round.",
        }
    else:
        return {
            "status": "waiting_for_players",
            "message": f"Waiting for {total_players - players_answered} players to answer.",
        }


@router.post("/{game_id}/player/{player_id}/answer")
def route_add_answer(
    game_id: int, player_id: int, player_answer: str, db: Depends(get_db)
):
    """
    Function that updates the player's guess in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")

        # Get game type data
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    bag = game_type.bag

    # Check if bag is red or blue
    balls_counter = Counter(bag)
    if balls_counter["R"] > balls_counter["B"]:
        correct_answer = "R"
    elif balls_counter["R"] < balls_counter["B"]:
        correct_answer = "B"

    # Check round progress
    game_answer = db.query(GameAnswer).filter_by(id=game_id).one_or_none()
    if not game_answer:
        current_round = 1
    else:
        current_round = game_answer.round

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

    return {"status": "New answer recorded"}
