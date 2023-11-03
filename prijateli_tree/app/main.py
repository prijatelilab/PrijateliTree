import glob
import json
import os
from pathlib import Path
from typing import Annotated, List

from fastapi import Depends, FastAPI, Header, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_localization import TranslateJsonResponse
from fastapi_login import LoginManager
from sqlalchemy import or_
from sqlalchemy.orm import Session

from prijateli_tree.app.config import config
from prijateli_tree.app.database import Base, User, engine, get_db
from prijateli_tree.app.routers import administration, games
from prijateli_tree.app.schemas import LanguageTranslatableSchema
from prijateli_tree.app.utils.constants import (
    FILE_MODE_READ,
    KEY_ENV,
    KEY_LOGIN_SECRET,
    LANGUAGE_ALBANIAN,
    LANGUAGE_ENGLISH,
    LANGUAGE_MACEDONIAN,
    LANGUAGE_TURKISH,
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
    STANDARD_ENCODING,
)


Base.metadata.create_all(bind=engine)

config = config[os.getenv(KEY_ENV)]

app = FastAPI(debug=config.DEBUG)

base_dir = Path(__file__).resolve().parent

app.mount(
    "/static", StaticFiles(directory=str(Path(base_dir, "static"))), name="static"
)
templates = Jinja2Templates(directory=str(Path(base_dir, "templates")))


login_manager = LoginManager(os.getenv(KEY_LOGIN_SECRET), "/admin/login")


@login_manager.user_loader()
def query_user(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(User)
        .filter_by(id=user_id)
        .filter(or_(User.role == ROLE_ADMIN, User.role == ROLE_SUPER_ADMIN))
        .one_or_none()
    )


languages = {}
for lang in glob.glob("languages/*.json"):
    lang_code = lang.split("\\")[1].split(".")[0]

    with open(lang, FILE_MODE_READ, encoding=STANDARD_ENCODING) as file:
        languages[lang_code] = json.load(file)

app.include_router(
    administration.router,
    prefix="/admin",
    tags=["admin"],
)
app.include_router(
    games.router,
    prefix="/games",
    tags=["games"],
)


@app.post(
    "/language",
    response_class=TranslateJsonResponse,
    response_model=List[LanguageTranslatableSchema],
)
def set_language(accept_language: Annotated[str | None, Header()] = None) -> Response:
    if accept_language in [
        LANGUAGE_ENGLISH,
        LANGUAGE_TURKISH,
        LANGUAGE_MACEDONIAN,
        LANGUAGE_ALBANIAN,
    ]:
        config.LANGUAGE = accept_language
    else:
        config.LANGUAGE = LANGUAGE_ENGLISH

    return JSONResponse(content={"message": "It done worked"})


@app.get("/", response_class=HTMLResponse)
def funky(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})
