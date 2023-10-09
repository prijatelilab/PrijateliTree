import os
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware

from prijateli_tree.app.controllers.administration import stuff
from prijateli_tree.app.controllers.games import (
    integrated_game,
    segregated_game,
    self_selected_game,
)
from prijateli_tree.app.models.database import Session
from prijateli_tree.app.utils.constants import (
    KEY_DATABASE_URI,
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SEGREGATED,
)


app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.getenv(KEY_DATABASE_URI))


@app.get("/")
def funky():
    return {"Hello": "World"}


@app.get("/administration")
def admin_access():
    stuff()


@app.get("/game/{game_id}")
def game_access(game_id: int):
    return {"game_id": game_id}


@app.get("/game/{game_id}/player/{player_id}")
def game_player_access(game_id: int, player_id: int):
    game = Session.query().filter_by(id=game_id).one_or_none()
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
