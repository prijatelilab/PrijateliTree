import random
from collections import Counter
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from prijateli_tree.app.database import Game, GameAnswer, GameType, Player, SessionLocal
from prijateli_tree.app.schemas import GameCreate, PlayerCreate
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
    if balls_counter["R"] > balls_counter["B"]:
        correct_answer = "R"
    elif balls_counter["R"] < balls_counter["B"]:
        correct_answer = "B"

    return correct_answer


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
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")

        # Get game type data
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    bag = game_type.bag

    correct_answer = get_bag_color(bag)

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


@router.get("/{game_id}/player/{player_id}/answer")
def get_previous_answers(
    game_id: int, player_id: int, game_type: str, db: Session = Depends(get_db)
):
    """
    Function that returns the player's previous answer
    from the last round, along with the answers of their neighbors
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")
    total_players = db.query(Player).filter_by(game_id=game_id).count()
    total_answers = db.query(GameAnswer).filter_by(game_id=game_id).count()
    current_round = total_answers // total_players + 1

    if current_round == 1:
        raise HTTPException(status_code=400, detail="No previous answers")

    else:
        last_round = current_round - 1

    # Get the player's previous answer
    player_answer_obj = (
        db.query(GameAnswer)
        .filter_by(game_id=game_id, player_id=player_id, round=last_round)
        .one_or_none()
    )

    player_answer = player_answer_obj.player_answer

    # Get the player's neighbors
    player = (
        db.query(Player).filter_by(game_id=game_id, user_id=player_id).one_or_none()
    )
    player_position = player.position

    # Use game utils to get the player's neighbors
    game_util = GameUtil(game_type)
    neighbors = game_util.neighbors[player_position]

    # Get the neighbors' previous answers
    neighbor_1_answer_obj = (
        db.query(GameAnswer)
        .filter_by(game_id=game_id, round=last_round, position=neighbors[0])
        .one_or_none()
    )

    neighbor_1_answer = neighbor_1_answer_obj.player_answer

    neighbor_2_answer_obj = (
        db.query(GameAnswer)
        .filter_by(game_id=game_id, round=last_round, position=neighbors[1])
        .one_or_none()
    )

    neighbor_2_answer = neighbor_2_answer_obj.player_answer

    return {
        "your_previous_answer": player_answer,
        "neighbor_1_previous_answer": neighbor_1_answer,
        "neighbor_2_previous_answer": neighbor_2_answer,
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
        raise HTTPException(status_code=400, detail="Player is not in the game")

    # Get game type data
    game_type = db.query(GameType).filter_by(id=game.game_type_id).one_or_none()
    bag = game_type.bag

    # Check if bag is red or blue
    correct_answer = get_bag_color(bag)

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
        route_add_answer(game_id, player_id, ball, db, current_round)

    else:
        get_previous_answers(game_id, player_id, db)
        # Show the player the previous round's answer
        # Show the neighbor's answers from the previous round
        # Update the player's answer if they want to
        pass
