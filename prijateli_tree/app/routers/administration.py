import logging
import os
import random
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from prijateli_tree.app.database import (
    Game,
    GameAnswer,
    GamePlayer,
    GameSession,
    GameSessionPlayer,
    GameType,
    RandomGroup,
    SessionLocal,
    User,
)
from prijateli_tree.app.utils.administration import Hasher, show_network, round_denars
from prijateli_tree.app.utils.constants import (
    DENAR_FACTOR,
    KEY_LOGIN_SECRET,
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SEGREGATED,
    NETWORK_TYPE_SELF_SELECTED,
    NUMBER_OF_GAMES,
    NUMBER_OF_PRACTICE_GAMES,
    NUMBER_OF_ROUNDS,
    NUMBER_OF_SELF_SELECTED_GAMES,
    ROLE_ADMIN,
    ROLE_STUDENT,
    ROLE_SUPER_ADMIN,
    ROUNDS_ARRAY,
    WINNING_SCORES,
    WINNING_WEIGHTS,
)
from prijateli_tree.app.utils.games import (
    raise_exception_if_none,
    raise_exception_if_not,
)


base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))
templates.env.globals["URL"] = URL

logger = logging.getLogger()


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
def query_user(user_uuid: int, db_session: Session) -> User | None:
    return db_session.query(User).filter_by(uuid=user_uuid).one_or_none()


@router.get("/", response_class=HTMLResponse)
def admin_page(user=Depends(login_manager.optional)) -> RedirectResponse:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)
    else:
        return RedirectResponse("dashboard", status_code=HTTPStatus.FOUND)


@router.get("/login", response_class=HTMLResponse)
def admin_login(request: Request) -> Response:
    return templates.TemplateResponse(
        "administration/admin_login.html", {"request": request}
    )


@router.post("/login")
def confirm_login(
    request: Request,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: Session = Depends(get_db),
) -> Response:
    user = (
        db.query(User)
        .filter(func.lower(User.email) == email.lower())
        .filter((User.role == ROLE_ADMIN) | (User.role == ROLE_SUPER_ADMIN))
        .one_or_none()
    )
    if user is None or not Hasher.verify_password(
        password, str(user.hashed_password)
    ):
        logger.info(f"User submitted invalid credentials: {email}")
        return templates.TemplateResponse(
            "administration/admin_login.html",
            {"request": request, "error": "Please submit valid credentials."},
        )

    token = login_manager.create_access_token(data={"sub": str(user.uuid)})
    response = RedirectResponse(url="dashboard", status_code=HTTPStatus.FOUND)
    login_manager.set_cookie(response, token)
    return response


@router.get("/logout", response_class=HTMLResponse)
def logout() -> RedirectResponse:
    resp = RedirectResponse(url="login", status_code=HTTPStatus.FOUND)
    login_manager.set_cookie(resp, "")
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    success: str = "",
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
) -> Response:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    sessions = db.query(GameSession).all()
    students = db.query(User).filter_by(role=ROLE_STUDENT).all()
    session_players = db.query(GameSessionPlayer).all()

    for sp in session_players:
        sp.denars = round_denars(sp.points, DENAR_FACTOR)

    student_dict = {}
    for s in students:
        student_dict[s.id] = s

    for s in sessions:
        players: [str] = []
        for p in s.players:
            players.append(student_dict[p.user_id].name_str)
        s.player_string = ", ".join(players)

    return templates.TemplateResponse(
        "administration/admin_dashboard.html",
        {
            "request": request,
            "success": success,
            "user": user,
            "sessions": sessions,
            "students": students,
            "student_dict": student_dict,
            "session_players": session_players
        },
    )


@router.get("/session", response_class=HTMLResponse)
def dashboard_create_session(
    request: Request,
    error: str = "",
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
) -> Response:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    students = db.query(User).filter_by(role=ROLE_STUDENT).all()

    return templates.TemplateResponse(
        "administration/create_session.html",
        {
            "request": request,
            "error": error,
            "user": user,
            "students": students,
        },
    )


@router.post("/session", response_class=HTMLResponse)
def create_session(
    player_one: Annotated[int, Form()],
    player_two: Annotated[int, Form()],
    player_three: Annotated[int, Form()],
    player_four: Annotated[int, Form()],
    player_five: Annotated[int, Form()],
    player_six: Annotated[int, Form()],
    session_key: Annotated[str, Form()],
    num_games: int = NUMBER_OF_GAMES,
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    if num_games is None:
        num_games = NUMBER_OF_GAMES
        logging.info(f"Setting number of games to {num_games}")

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
    logging.info("Setting up session")
    session = GameSession(
        created_by=user.id,
        session_key=session_key,
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

    game = None
    previous_game = None

    for i in range(NUMBER_OF_PRACTICE_GAMES):
        if game:
            previous_game = game

        game_type_id = (
            db.query(GameType)
            .filter_by(
                network=[NETWORK_TYPE_INTEGRATED, NETWORK_TYPE_SEGREGATED][i],
                names_hidden=[True, False][i],
            )
            .first()
            .id
        )

        game = Game(
            created_by=user.id,
            game_session_id=session.id,
            game_type_id=game_type_id,
            rounds=NUMBER_OF_ROUNDS,
            practice=True,
            winning_score=0,
            is_network_visible=False,
        )

        db.add(game)
        db.commit()
        db.refresh(game)

        if previous_game:
            previous_game.next_game_id = game.id
            db.commit()

        add_players_to_practice_game(lang_dict, game, session, db)

        db.commit()
        db.refresh(game)

    create_session_games(session, game, db)

    redirect_url = URL("/admin/dashboard").include_query_params(
        success=f"Your session (Key: {session.session_key}) and first "
        f"game (ID: {game.id}) have been created!"
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )


def create_session_games(
    session,
    game,
    db: Session = Depends(get_db),
) -> None:
    regular_game_count = session.num_games - NUMBER_OF_SELF_SELECTED_GAMES

    for i in range(session.num_games):
        previous_game = game

        if i < regular_game_count:
            game_types = (
                db.query(GameType)
                .filter(
                    GameType.network.in_(
                        [NETWORK_TYPE_INTEGRATED, NETWORK_TYPE_SEGREGATED]
                    )
                )
                .all()
            )
            is_network_visible = show_network()

        else:
            game_types = (
                db.query(GameType)
                .filter(
                    GameType.network.in_([NETWORK_TYPE_SELF_SELECTED]),
                    GameType.names_hidden.is_(False),
                )
                .all()
            )
            is_network_visible = False

        game_type = random.choice(game_types)
        n_rounds = random.choice(ROUNDS_ARRAY)

        # Add score
        random_score = random.choices(WINNING_SCORES, weights=WINNING_WEIGHTS)[
            0
        ]

        game = Game(
            created_by=session.created_by,
            game_session_id=session.id,
            game_type_id=game_type.id,
            rounds=n_rounds,
            winning_score=random_score,
            is_network_visible=is_network_visible,
        )

        db.add(game)
        db.commit()
        db.refresh(game)

        previous_game.next_game_id = game.id
        db.commit()

        add_players_to_game(previous_game, game, db)


def add_players_to_practice_game(lang_dict, game, session, db):
    user_ids = []
    session_players = []
    user_lists = lang_dict.values()
    for user_list in user_lists:
        for user in user_list:
            user_ids.append(user.id)
            session_players.append(
                [sp for sp in session.players if sp.user_id == user.id][0]
            )

    rand_bag = random.sample(game.game_type.bag, len(game.game_type.bag))

    for i, session_player in enumerate(session_players):
        db.add(
            GamePlayer(
                created_by=session.created_by,
                game_id=game.id,
                user_id=user_ids[i],
                session_player_id=session_player.id,
                position=i + 1,
                initial_ball=rand_bag[i],
            )
        )

    db.commit()
    db.refresh(game)


def add_players_to_game(previous_game, game, db) -> None:
    """ """
    # randomize location in network conditional on language
    # one group is always in 1-2-3 and the other 4-5-6
    group_1 = [p for p in previous_game.players if p.position in (1, 2, 3)]
    random.shuffle(group_1)

    group_2 = [p for p in previous_game.players if p.position in (4, 5, 6)]
    random.shuffle(group_2)

    pos_players = group_1 + group_2
    rand_bag = random.sample(game.game_type.bag, len(game.game_type.bag))

    for i, player in enumerate(pos_players):
        db.add(
            GamePlayer(
                created_by=game.created_by,
                game_id=game.id,
                user_id=player.user_id,
                session_player_id=player.session_player_id,
                position=i + 1,
                initial_ball=rand_bag[i],
            )
        )
    db.commit()
    db.refresh(game)


@router.get("/add_students", response_class=HTMLResponse)
def dashboard_add_students(
    request: Request,
    user=Depends(login_manager.optional),
) -> Response:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    return templates.TemplateResponse(
        "administration/admin_bulk_add.html",
        {
            "request": request,
            "user": user,
        },
    )


@router.post("/add_students", response_class=HTMLResponse)
def add_students(
    file: UploadFile = File(...),
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    students_added = 0
    try:
        student_df = pd.read_csv(file.file)
        expected_fields = [
            "first_name",
            "last_name",
            "grade_level",
            "high_school_id",
            "language_id",
            "qualtrics_id",
        ]
        raise_exception_if_not(
            all([x in student_df.columns for x in expected_fields]),
            detail="Upload file is missing expected fields",
        )

        for _, student in student_df.iterrows():
            student_exists = (
                db.query(User)
                .filter_by(qualtrics_id=student.qualtrics_id)
                .one_or_none()
            )
            if student_exists is None and student.qualtrics_id is not None:
                student_in = User(
                    created_by=user.id,
                    **student,
                    role="student",
                )
                db.add(student_in)
                students_added += 1
        db.commit()

    except Exception as e:
        # Rollback the transaction if an error occurs
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: {str(e)}"
        )

    finally:
        file.file.close()

    redirect_url = URL("/admin/dashboard").include_query_params(
        success=f"{students_added} students added to the database."
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )


@router.post("/add_group_assignments", response_class=HTMLResponse)
def add_group_assignments(
    file: UploadFile = File(...),
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    try:
        group_df = pd.read_csv(file.file)
        expected_fields = ["user_id", "group_id"]
        raise_exception_if_not(
            all([x in group_df.columns for x in expected_fields]),
            detail="Upload file is missing expected fields",
        )
        groups_added = 0
        for _, assignment in group_df.iterrows():
            student_exists = (
                db.query(User).filter_by(id=assignment.user_id).one_or_none()
            )
            raise_exception_if_none(
                student_exists,
                detail=f"student {assignment.user_id} not found in db.",
            )

            group_assignment_in = RandomGroup(
                # created_by=user.id,
                user_id=assignment.user_id,
                group_id=assignment.group_id.lower(),
            )
            db.add(group_assignment_in)
            groups_added += 1

        db.commit()

    except Exception as e:
        # Rollback the transaction if an error occurs
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: {str(e)}"
        )

    finally:
        file.file.close()

    redirect_url = URL("/admin/dashboard").include_query_params(
        success=f"{groups_added} group assignments added to the database."
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )


@router.get("/dashboard_analysis", response_class=HTMLResponse)
def analysis_dashboard(
    request: Request,
    user=Depends(login_manager.optional),
    db: Session = Depends(get_db),
) -> Response:
    if user is None:
        return RedirectResponse("login", status_code=HTTPStatus.FOUND)

    games = db.query(Game).all()
    answers = db.query(GameAnswer).all()
    students = db.query(User).filter_by(role=ROLE_STUDENT).all()
    game_players = db.query(GamePlayer).all()
    # student_dict = {}
    # for s in students:
    #     student_dict[s.id] = s

    # for s in sessions:
    #    players: [str] = []
    #    for p in s.players:
    #        players.append(student_dict[p.user_id].name_str)
    #   s.player_string = ", ".join(players)

    return templates.TemplateResponse(
        "administration/analysis_dashboard.html",
        {
            "request": request,
            "user": user,
            "games": games,
            "students": students,
            "game_players": game_players,
            "answers": answers,
        },
    )
