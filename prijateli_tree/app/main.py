import logging
import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_localization import TranslateJsonResponse

from prijateli_tree.app.config import config
from prijateli_tree.app.routers import administration, games
from prijateli_tree.app.utils.constants import (
    KEY_ENV,
    LANGUAGE_ALBANIAN,
    LANGUAGE_ENGLISH,
    LANGUAGE_MACEDONIAN,
    LANGUAGE_TURKISH,
)


config = config[os.getenv(KEY_ENV)]
logging.basicConfig(level=config.LOG_LEVEL, format=config.LOGGING_FORMAT)
logger = logging.getLogger()

app = FastAPI(debug=config.DEBUG)

base_dir = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(Path(base_dir, "static"))),
    name="static",
)
templates = Jinja2Templates(directory=str(Path(base_dir, "templates")))

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
logger.debug("Routers loaded and static files mounted.")


@app.post(
    "/language",
    response_class=TranslateJsonResponse,
)
def set_language(
    accept_language: Annotated[str | None, Header()] = None
) -> JSONResponse:
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
def home(request: Request) -> Response:
    return templates.TemplateResponse("home_page.html", {"request": request})


@app.get("/ready", response_class=HTMLResponse)
def ready(request: Request) -> Response:
    return templates.TemplateResponse("ready.html", {"request": request})


@app.get("/waiting", response_class=HTMLResponse)
def waiting(request: Request) -> Response:
    return templates.TemplateResponse("waiting.html", {"request": request})
