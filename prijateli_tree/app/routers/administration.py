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
    GameSession,
    GameSessionPlayer,
    GameType,
    SessionLocal,
    User,
)
from prijateli_tree.app.utils.constants import (
    KEY_LOGIN_SECRET,
    NETWORK_TYPE_INTEGRATED,
    NUMBER_OF_ROUNDS,
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
    sessions = db.query(GameSession).all()
    students = db.query(User).filter_by(role=ROLE_STUDENT).all()
    denir_transactions = db.query(Denirs).all()
    student_dict = {}
    for s in students:
        student_dict[s.id] = s

    for s in sessions:
        players = []
        for p in s.players:
            players.append(student_dict[p.user_id].name_str)
        s.player_string = ", ".join(players)

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "success": success,
            "user": user,
            "game_types": game_types,
            "sessions": sessions,
            "students": students,
            "student_dict": student_dict,
            "transactions": denir_transactions,
        },
    )


@router.get("/session", response_class=HTMLResponse)
def dashboard_create_session(
    request: Request,
    error: str = "",
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    students = db.query(User).filter_by(role=ROLE_STUDENT).all()

    return templates.TemplateResponse(
        "create_session.html",
        {
            "request": request,
            "error": error,
            "user": user,
            "students": students,
        },
    )


@router.post("/session")
def create_session(
    num_games: Annotated[int, Form()],
    player_one: Annotated[int, Form()],
    player_two: Annotated[int, Form()],
    player_three: Annotated[int, Form()],
    player_four: Annotated[int, Form()],
    player_five: Annotated[int, Form()],
    player_six: Annotated[int, Form()],
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
):
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    player_ids = [
        player_one,
        player_two,
        player_three,
        player_four,
        player_five,
        player_six,
    ]

    players = []
    for p_id in player_ids:
        players.append(db.query(User).filter_by(id=p_id).one())

    lang_dict = {}
    for p in players:
        if p.language.abbr in lang_dict:
            lang_dict[p.language.abbr].append(p)
        else:
            lang_dict[p.language.abbr] = [p]

    for v in lang_dict.values():
        if len(v) != 3:
            redirect_url = URL("/admin/session").include_query_params(
                error="A session must contain exactly 3 players of different "
                "ethnicities."
            )
            return RedirectResponse(
                redirect_url,
                status_code=HTTPStatus.FOUND,
            )

    if len(set(player_ids)) != 6:
        redirect_url = URL("/admin/session").include_query_params(
            error="A session cannot contain the same student twice."
        )
        return RedirectResponse(
            redirect_url,
            status_code=HTTPStatus.FOUND,
        )

    session = GameSession(
        created_by=user.id,
        num_games=num_games,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    for p_id in player_ids:
        db.add(
            GameSessionPlayer(
                created_by=user.id,
                session_id=session.id,
                user_id=p_id,
            )
        )

    db.commit()
    db.refresh(session)

    game = Game(
        created_by=user.id,
        game_session_id=session.id,
        game_type_id=db.query(GameType)
        .filter_by(network=NETWORK_TYPE_INTEGRATED, names_hidden=False)
        .first()
        .id,
        rounds=NUMBER_OF_ROUNDS,
        practice=True,
    )
    db.add(game)
    db.commit()
    db.refresh(game)

    position = 1
    for p_list in lang_dict.values():
        for p in p_list:
            session_player = [
                sp for sp in session.players if sp.user_id == p.id
            ][0]
            db.add(
                GamePlayer(
                    created_by=user.id,
                    game_id=game.id,
                    user_id=p.id,
                    session_player_id=session_player.id,
                    position=position,
                )
            )
            position += 1

    db.commit()

    redirect_url = URL("/admin/dashboard").include_query_params(
        success=f"Your session (ID: {session.id}) and first game (ID: {game.id}) have been created!"
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )
