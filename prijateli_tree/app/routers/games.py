import random
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


def integrated_game(game_id: int, player_id: int, db: Session = Depends(get_db)):
    """
    Logic for handling the integrated game
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")

    num_rounds = game.rounds
    game_type_id = game.game_type_id
    # Check if the player is in the game
    existing_player = (
        db.query(Player).filter_by(game_id=game_id, user_id=player_id).one_or_none()
    )
    if not existing_player:
        raise HTTPException(status_code=400, detail="Player is not in the game")

    # Get game type data
    game_type = db.query(GameType).filter_by(id=game_type_id).one_or_none()
    bag = game_type.bag
    if not game_type:
        raise HTTPException(status_code=400, detail="Game type not found")

    # Get current round
    game_answer = db.query(GameAnswer).filter_by(id=game_id).one_or_none()
    if not game_answer:
        current_round = 1
    else:
        current_round = game_answer.round

    if current_round > num_rounds:
        raise HTTPException(status_code=400, detail="Game is over")

    if current_round == 1:
        # Pick a random letter from the bag and show it to the player
        ball = random.choice(bag)
        print(ball)


@router.post("/{game_id}/player/{player_id}/answer")
def route_add_answer(game_id: int, player_id: int, player_answer: str):
    pass
