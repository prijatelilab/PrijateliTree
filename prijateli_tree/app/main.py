import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from prijateli_tree.app.config import config
from prijateli_tree.app.routers import administration, games
from prijateli_tree.app.utils.constants import KEY_ENV


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


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> Response:
    return templates.TemplateResponse("home_page.html", {"request": request})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 405 or exc.status_code == 404:
        suggested_path = request["path"].split("/")
        suggested_path = [p for p in suggested_path if p != ""]
        suggested_path[-1] = "round"
        logging.info(f'Status {exc.status_code}: {exc.detail}'  )
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "suggested_path": "/".join(suggested_path),
                "exc": exc,
            },
        )

    # Pass other exceptions as they are
    raise exc
