from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from prijateli_tree.app.database import Base, Game, SessionLocal, engine
from prijateli_tree.app.utils.constants import (
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SEGREGATED,
)
from prijateli_tree.app.views.administration import stuff
from prijateli_tree.app.views.games import (
    add_player_to_game,
    create_new_game,
    integrated_game,
    segregated_game,
    self_selected_game,
)


Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def funky():
    return {"Hello": "World"}


@app.get("/administration")
def route_admin_access():
    stuff()


@app.post("/game/")
def route_create_game(game_type: int, user_id: int, num_rounds: int, practice: bool):
    new_game_id = create_new_game(game_type, user_id, num_rounds, practice)
    return {"status": "success", "game_id": new_game_id}


@app.post("/game/{game_id}/player/")
def route_add_player(
    game_id: int, user_id: int, position: int, name_hidden: bool = False
):
    new_player_id = add_player_to_game(game_id, user_id, position, name_hidden)
    return {"status": "success", "player_id": new_player_id}


@app.get("/game/{game_id}")
def route_game_access(game_id: int):
    game = Game.query().filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")
    return {"game_id": game_id}


@app.get("/game/{game_id}/player/{player_id}")
def route_game_player_access(game_id: int, player_id: int):
    game = Game.query().filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")

    if len([player for player in game.players if player.user_id == player_id]) != 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not found in game"
        )

    if game.session_type.network == NETWORK_TYPE_INTEGRATED:
        integrated_game(game, player_id)
    elif game.session_type.network == NETWORK_TYPE_SEGREGATED:
        segregated_game(game, player_id)
    else:
        self_selected_game(game, player_id)


@app.post("game/{game_id}/player/{player_id}/answer")
def route_add_answer(game_id: int, player_id: int, player_answer: str):
    pass
