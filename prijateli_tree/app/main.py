import glob
import json
import os
from http import HTTPStatus
from typing import Annotated, List

from fastapi import FastAPI, Header, HTTPException
from fastapi_localization import TranslateJsonResponse

from prijateli_tree.app.config import config
from prijateli_tree.app.database import Base, Game, SessionLocal, engine
from prijateli_tree.app.schemas import LanguageTranslatableSchema
from prijateli_tree.app.utils.constants import (
    FILE_MODE_READ,
    KEY_ENV,
    LANGUAGE_ALBANIAN,
    LANGUAGE_ENGLISH,
    LANGUAGE_MACEDONIAN,
    LANGUAGE_TURKISH,
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SEGREGATED,
    STANDARD_ENCODING,
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

config = config[os.getenv(KEY_ENV)]

active_language = LANGUAGE_ENGLISH

languages = {}
for lang in glob.glob("languages/*.json"):
    lang_code = lang.split("\\")[1].split(".")[0]

    with open(lang, FILE_MODE_READ, encoding=STANDARD_ENCODING) as file:
        languages[lang_code] = json.load(file)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/language",
    response_class=TranslateJsonResponse,
    response_model=List[LanguageTranslatableSchema],
)
def set_language(accept_language: Annotated[str | None, Header()] = None):
    if accept_language in [
        LANGUAGE_ENGLISH,
        LANGUAGE_TURKISH,
        LANGUAGE_MACEDONIAN,
        LANGUAGE_ALBANIAN,
    ]:
        config.LANGUAGE = accept_language
    else:
        config.LANGUAGE = LANGUAGE_ENGLISH

    return HTTPStatus.OK


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
