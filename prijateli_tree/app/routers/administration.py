import os
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from prijateli_tree.app.database import (
    Denirs,
    Game,
    GamePlayer,
    GameType,
    SessionLocal,
    User,
)
from prijateli_tree.app.utils.constants import (
    KEY_LOGIN_SECRET,
    ROLE_ADMIN,
    ROLE_STUDENT,
    ROLE_SUPER_ADMIN,
)


base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))
templates.env.globals["URL"] = URL


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()

login_manager = LoginManager(
    os.getenv(KEY_LOGIN_SECRET),
    "/login",
    use_cookie=True,
)


@login_manager.user_loader(db_session=SessionLocal())
def query_user(user_uuid: int, db_session: Session):
    return db_session.query(User).filter_by(uuid=user_uuid).one_or_none()


@router.get("/", response_class=HTMLResponse)
def admin_page(user=Depends(login_manager.optional)):
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)
    else:
        return RedirectResponse("dashboard", status_code=HTTPStatus.FOUND)


@router.get("/login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.post("/login")
def confirm_login(
    request: Request,
    first_name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter_by(
            email=email.lower(), first_name=first_name, last_name=last_name
        )
        .filter((User.role == ROLE_ADMIN) | (User.role == ROLE_SUPER_ADMIN))
        .one_or_none()
    )
    if user is None:
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": "Please submit valid credentials."},
        )

    token = login_manager.create_access_token(data={"sub": str(user.uuid)})
    response = RedirectResponse(url="dashboard", status_code=HTTPStatus.FOUND)
    login_manager.set_cookie(response, token)
    return response


@router.get("/logout", response_class=HTMLResponse)
def logout():
    resp = RedirectResponse(url="login", status_code=HTTPStatus.FOUND)
    login_manager.set_cookie(resp, "")
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    success: str = "",
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    game_types = db.query(GameType).all()
    games = db.query(Game).all()
    students = db.query(User).filter_by(role=ROLE_STUDENT).all()
    denir_transactions = db.query(Denirs).all()

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "success": success,
            "user": user,
            "game_types": game_types,
            "games": games,
            "students": students,
            "transactions": denir_transactions,
        },
    )


@router.get("/game", response_class=HTMLResponse)
def dashboard_create_game(
    request: Request,
    error: str = "",
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    game_types = db.query(GameType).all()
    students = db.query(User).filter_by(role=ROLE_STUDENT).all()

    return templates.TemplateResponse(
        "create_game.html",
        {
            "request": request,
            "error": error,
            "user": user,
            "game_types": game_types,
            "students": students,
        },
    )


@router.post("/game")
def create_game(
    game_type: Annotated[str, Form()],
    rounds: Annotated[int, Form()],
    pos_one: Annotated[int, Form()],
    pos_two: Annotated[int, Form()],
    pos_three: Annotated[int, Form()],
    pos_four: Annotated[int, Form()],
    pos_five: Annotated[int, Form()],
    pos_six: Annotated[int, Form()],
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    pos_players = [pos_one, pos_two, pos_three, pos_four, pos_five, pos_six]

    if len(set(pos_players)) != 6:
        redirect_url = URL("/admin/game").include_query_params(
            error="A game cannot contain the same student at two different positions."
        )
        return RedirectResponse(
            redirect_url,
            status_code=HTTPStatus.FOUND,
        )

    game = Game(
        created_by=user.id,
        game_type_id=game_type,
        rounds=rounds,
    )

    db.add(game)
    db.commit()
    db.refresh(game)

    for i in range(0, len(pos_players)):
        db.add(
            GamePlayer(
                created_by=user.id,
                game_id=game.id,
                user_id=pos_players[i],
                position=i + 1,
            )
        )

    db.commit()
    db.refresh(game)

    redirect_url = URL("/admin/dashboard").include_query_params(
        success=f"Your game (ID: {game.id}) has been successfully created!"
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )
