import os
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware

from prijateli_tree.app.controllers.administration import stuff
from prijateli_tree.app.models.database import Session
from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


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
    session = Session.query().filter_by(id=game_id).one_or_none()
    if session is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="game not found")

    return {"game_id": game_id, "player_id": player_id}
