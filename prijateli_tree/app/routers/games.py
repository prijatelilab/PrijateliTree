import glob
import json
import logging
import random
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from prijateli_tree.app.database import (
    Game,
    GameAnswer,
    GamePlayer,
    GameSession,
    GameSessionPlayer,
    PlayerNetwork,
    User,
    get_db,
)
from prijateli_tree.app.utils.constants import (
    DENAR_FACTOR,
    FILE_MODE_READ,
    NETWORK_TYPE_INTEGRATED,
    NETWORK_TYPE_SELF_SELECTED,
    POST_SURVEY_LINK,
    PRE_SURVEY_LINK,
    STANDARD_ENCODING,
)
from prijateli_tree.app.utils.games import (
    GameUtil,
    check_if_neighbors,
    did_player_win,
    get_bag_color,
    get_current_round,
    get_game_and_player,
    get_header_data,
    get_lang_from_player_id,
    get_previous_answers,
    get_session_player_from_player,
    is_real_game_transition,
    raise_exception_if_none,
    raise_exception_if_not,
)

from prijateli_tree.app.utils.administration import round_denars

logger = logging.getLogger()
router = APIRouter()

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))

languages = {}
for lang in glob.glob("prijateli_tree/app/languages/*.json"):
    with open(lang, FILE_MODE_READ, encoding=STANDARD_ENCODING) as file:
        languages.update(json.load(file))
logger.debug("Language files imported.")


###############################
#
#        BEGIN API
#
###############################


@router.get("/sessions", response_class=HTMLResponse)
def choose_session_id(request: Request) -> Response:
    return templates.TemplateResponse(
        "games/new_session.html",
        context={"request": request, "session_key": -1},
    )


@router.get("/session/{session_key}", response_class=HTMLResponse)
def choose_session_players(
    request: Request, session_key: str, db: Session = Depends(get_db)
) -> Response:
    session = (
        db.query(GameSession)
        .filter_by(session_key=session_key.lower())
        .order_by(desc("created_at"))
        .first()
    )
    if session is None:
        return templates.TemplateResponse(
            "games/new_session.html",
            context={
                "request": request,
                "session_key": -1,
                "message": "Session key not found. Make sure the key is correct.",
            },
        )

    games = db.query(Game).filter_by(game_session_id=session.id).all()
    raise_exception_if_not(games, "session not found or games not created")

    first_game = [
        game for game in games if game.id == min([game.id for game in games])
    ][0]
    players = first_game.players

    return templates.TemplateResponse(
        "games/new_session.html",
        context={
            "request": request,
            "players": players,
            "game_id": first_game.id,
        },
    )


@router.get("/get_session_players/{session_key}", response_class=JSONResponse)
def get_session_players(
    request: Request, session_key: str, db: Session = Depends(get_db)
) -> Response:
    session = (
        db.query(GameSession)
        .filter_by(session_key=session_key.lower())
        .order_by(desc("created_at"))
        .first()
    )
    if session is None:
        return JSONResponse(
            content={
                "request": request,
                "message": "Session key not found. Make sure the key is correct.",
            },
        )
    game = db.query(Game).filter_by(game_session_id=session.id).first()
    raise_exception_if_none(game, "session not found or games not created")
    players = [p.user.name_str for p in game.players]

    return JSONResponse(content={"players": players})


@router.get("/{game_id}/player/{player_id}/ready", response_class=HTMLResponse)
def start_session(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    _, player = get_game_and_player(game_id, player_id, db)
    template_text = languages[player.language.abbr]

    result = {
        "request": request,
        "player_id": player_id,
        "game_id": game_id,
        "name": player.user.name_str,
        "text": template_text,
    }

    return templates.TemplateResponse("games/ready.html", result)


@router.get(
    "/{game_id}/player/{player_id}/start_of_game", response_class=HTMLResponse
)
def start_of_game(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Function that returns the start of game page and
    template.
    """
    template_text = languages[get_lang_from_player_id(player_id, db)]
    game, _ = get_game_and_player(game_id, player_id, db)

    result = {
        "request": request,
        "player_id": player_id,
        "game_id": game_id,
        "text": template_text,
        "game": {
            key: game.__dict__[key]
            for key in ["practice", "winning_score", "is_network_visible"]
        },
        "game_type": game.game_type.network,
        "is_real_game_transition": is_real_game_transition(game, db),
    }

    return templates.TemplateResponse("games/start_of_game.html", result)


@router.get(
    "/{game_id}/player/{player_id}/network", response_class=JSONResponse
)
def get_data_for_network(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    game, player = get_game_and_player(game_id, player_id, db)
    template_text = languages[player.language.abbr]
    is_integrated = game.game_type.network == NETWORK_TYPE_INTEGRATED

    if not game.game_type.names_hidden:
        players = [
            {
                "position": p.position,
                "this_player": p.id == player_id,
                "name": f"{p.user.first_name} {p.user.last_name}",
            }
            for p in game.players
        ]
    else:
        players = [
            {
                "position": p.position,
                "this_player": p.id == player_id,
                "name": f"{p.position}",
            }
            for p in game.players
        ]
    # ensures consistent diagram on refresh
    random.seed(game_id * player_id)
    reverse = random.random() > 0.5
    reflect = random.random() > 0.5
    return {
        "text": template_text,
        "data": players,
        "is_integrated": is_integrated,
        "reverse": reverse,
        "reflect": reflect,
    }


@router.get("/{game_id}/player/{player_id}/round")
def view_round(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Function that returns the current round
    """
    game, player = get_game_and_player(game_id, player_id, db)
    header = get_header_data(player, db)

    template_text = languages[player.language.abbr]
    current_round = get_current_round(game_id, db)
    template_data = {
        "practice_game": game.practice,
        "first_round": current_round == 1,
        "text": template_text,
        "player_id": player_id,
        "game_id": game_id,
        "completed_game": player.completed_game,
        "round_progress": f"{current_round}/??",
        **header,
    }
    # Get current round
    if current_round == 1:
        if game.game_type.network == NETWORK_TYPE_SELF_SELECTED:
            neighbors_exist = check_if_neighbors(player_id, db)
            if not neighbors_exist:
                redirect_url = request.url_for(
                    "choose_neighbors", game_id=game_id, player_id=player_id
                )
                return RedirectResponse(
                    url=redirect_url, status_code=HTTPStatus.FOUND
                )
        template_data["ball"] = player.initial_ball
    elif current_round > game.rounds:
        redirect_url = request.url_for(
            "end_of_game", game_id=game_id, player_id=player_id
        )
        return RedirectResponse(url=redirect_url, status_code=HTTPStatus.FOUND)
    else:
        template_data["previous_answers"] = get_previous_answers(
            game_id, player_id, db
        )

    return templates.TemplateResponse(
        "games/round.html", {"request": request, **template_data}
    )


@router.get("/{game_id}/player/{player_id}/choose_neighbors")
def choose_neighbors(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Function that will allow each player to choose their neighbors
    """
    game, player = get_game_and_player(game_id, player_id, db)
    template_text = languages[get_lang_from_player_id(player_id, db)]
    header = get_header_data(player, db)

    # Get number of neighbors the player has
    # We just use  the integrated network to get the number of neighbors
    game_util = GameUtil(NETWORK_TYPE_INTEGRATED)
    num_neighbors = len(game_util.neighbors[player.position])

    # Get the users of the players
    user_ids = [p.user_id for p in game.players]

    # Remove the current player from the list
    user_ids.remove(player.user_id)

    # Query users
    users = db.query(User).filter(User.id.in_(user_ids)).all()

    template_data = {
        "text": template_text,
        "player_id": player_id,
        "game_id": game_id,
        "num_neighbors": num_neighbors,
        "students": users,
        **header,
    }

    return templates.TemplateResponse(
        "games/choose_neighbors.html", {"request": request, **template_data}
    )


@router.post("/{game_id}/player/{player_id}/add_neighbors")
def add_neighbors(
    request: Request,
    game_id: int,
    player_id: int,
    player_one: Annotated[int, Form()],
    player_two: Annotated[int, Form()],
    player_three: Annotated[int, Form()] | None = Form(None),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Function that will add the neighbors to the database
    """
    # Get the players
    neighbor_player_ids = []
    for user_id in [player_one, player_two, player_three]:
        if user_id is not None:
            neighbor_player_ids.append(
                db.query(GamePlayer)
                .filter_by(user_id=user_id, game_id=game_id)
                .one_or_none()
                .id
            )

    if len(set(neighbor_player_ids)) != len(neighbor_player_ids):
        # Do not let them move forward if neighbor is duplicated
        redirect_url = request.url_for(
            "choose_neighbors", game_id=game_id, player_id=player_id
        )

        return RedirectResponse(
            url=redirect_url,
            status_code=HTTPStatus.FOUND,
        )

    for neighbor_id in neighbor_player_ids:
        new_neighbor = PlayerNetwork(
            game_id=game_id,
            player_id=player_id,
            neighbor_id=neighbor_id,
        )
        db.add(new_neighbor)
        db.commit()
        db.refresh(new_neighbor)

    redirect_url = request.url_for(
        "view_round", game_id=game_id, player_id=player_id
    )

    return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)


@router.post("/{game_id}/player/{player_id}/answer")
def route_add_answer(
    request: Request,
    game_id: int,
    player_id: int,
    player_answer: str = Form(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Function that updates the player's guess in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    raise_exception_if_none(game, detail="game not found")

    current_round = get_current_round(game_id, db)

    if (
        not db.query(GameAnswer)
        .filter_by(game_player_id=player_id, round=current_round)
        .one_or_none()
    ):
        # Getting correct answer and current round
        correct_answer = get_bag_color(game.game_type.bag)

        # Record the answer
        new_answer = GameAnswer(
            game_player_id=player_id,
            player_answer=player_answer,
            correct_answer=correct_answer,
            round=current_round,
        )

        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)

    redirect_url = request.url_for(
        "waiting", game_id=game_id, player_id=player_id
    )

    return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)


@router.get(
    "/{game_id}/player/{player_id}/all_set", response_class=JSONResponse
)
def all_set(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Determines if all players have submitted a guess in the current round
    """
    game, _ = get_game_and_player(game_id, player_id, db)
    n_answers = 0
    this_players_round = 0
    for player in game.players:
        if player.answers:
            this_round = max([a.round for a in player.answers])
            n_answers += this_round
            if player.id == player_id:
                this_players_round = this_round

    # if laggy internet, we don't want anyone stuck on the waiting screen
    ready = (
        n_answers % len(game.players) == 0
        or (n_answers / len(game.players)) > this_players_round
    )
    game_over = player.game.rounds == this_round
    return JSONResponse(content={"ready": ready, "game_over": game_over})


@router.get(
    "/{game_id}/player/{player_id}/waiting", response_class=HTMLResponse
)
def waiting(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Wait screen shows until all players are ready to move to the next section
    """
    game, player = get_game_and_player(game_id, player_id, db)
    template_text = languages[get_lang_from_player_id(player_id, db)]
    header = get_header_data(player, db)
    current_round = get_current_round(game_id, db)

    result = {
        "request": request,
        "game_id": game_id,
        "player_id": player_id,
        "text": template_text,
        "round_progress": f"{current_round}/??",
        "practice_game": game.practice,
        "completed_game": player.completed_game,
        **header,
    }

    return templates.TemplateResponse("games/waiting.html", result)


@router.put(
    "/{game_id}/player/{player_id}/update_score", response_class=JSONResponse
)
def update_score(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Function that updates the player's score in the database
    """
    game, player = get_game_and_player(game_id, player_id, db)
    if not player.completed_game:
        player.completed_game = True
        if not game.practice:
            session_player = get_session_player_from_player(player, db)
            game_status = did_player_win(game, player_id, db)
            session_player.correct_answers += game_status["is_correct"]
            session_player.points += (
                game_status["is_correct"] * game.winning_score
            )
        db.commit()
        db.refresh(player)

    return JSONResponse(content={"status": "success"})


@router.get("/{game_id}/player/{player_id}/survey", response_class=HTMLResponse)
def get_qualtrics(
    request: Request,
    player_id: int,
    game_id: int,
    db: Session = Depends(get_db),
) -> Response:
    _, player = get_game_and_player(game_id, player_id, db)

    if player.completed_game:
        survey_link = POST_SURVEY_LINK
    else:
        survey_link = PRE_SURVEY_LINK

    lang = player.language.abbr.upper()
    if lang == "SQ":
        lang = "SQI"
    cid = player.user.qualtrics_id

    if cid:
        survey_link = survey_link + "?Q_Language=" + lang + "&cid=" + cid
    else:
        survey_link = survey_link + "?Q_Language=" + lang

    return templates.TemplateResponse(
        "games/qualtrics.html",
        {
            "request": request,
            "player_id": player_id,
            "game_id": game_id,
            "survey_link": survey_link,
        },
    )


@router.get("/current_score/{player_id}", response_class=JSONResponse)
def route_get_score(
    request: Request,
    player_id: int,
    db: Session = Depends(get_db),
) -> JSONResponse:
    session_player_id = (
        db.query(GamePlayer).filter_by(id=player_id).one().session_player_id
    )

    session_player = (
        db.query(GameSessionPlayer)
        .filter_by(id=session_player_id)
        .one_or_none()
    )
    if session_player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="GameSessionPlayer not found",
        )
    return JSONResponse(content={"points": session_player.points})


@router.get(
    "/{game_id}/player/{player_id}/end_of_game", response_class=HTMLResponse
)
def end_of_game(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Function that returns the end of game page and
    template.
    """

    game, player = get_game_and_player(game_id, player_id, db)
    game_status = did_player_win(game, player_id, db)

    header = get_header_data(player, db)

    points = 0
    if game_status["is_correct"]:
        points = game.winning_score

    template_text = languages[player.language.abbr]

    result = {
        "request": request,
        "player_id": player_id,
        "game_id": game_id,
        "points": points,
        "text": template_text,
        "practice_game": game.practice,
        "completed_game": True,
        "player_answer": game_status["player_guess"],
        **header,
    }

    # add information about winning and ball colors
    result.update(game_status)

    return templates.TemplateResponse("games/end_of_game.html", result)


@router.get("/{game_id}/player/{player_id}/next_game")
def go_to_next_game(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Moves player to first round of next game or ends the session
    """
    game, player = get_game_and_player(game_id, player_id, db)

    if game.next_game_id is None:
        redirect_url = request.url_for(
            "get_qualtrics", game_id=game_id, player_id=player_id
        )
        return RedirectResponse(
            url=redirect_url, status_code=HTTPStatus.SEE_OTHER
        )

    next_player_id = (
        db.query(GamePlayer)
        .filter_by(user_id=player.user_id, game_id=game.next_game_id)
        .one()
        .id
    )

    raise_exception_if_none(next_player_id, detail="next player not found")

    # Check if this game is practice
    redirect_url = request.url_for(
        "start_of_game",
        game_id=game.next_game_id,
        player_id=next_player_id,
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )


@router.get(
    "/{game_id}/player/{player_id}/end_of_session",
    response_class=HTMLResponse,
)
def end_of_session(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Function that returns the end of session page and
    template.
    """
    game, player = get_game_and_player(game_id, player_id, db)
    session_player = get_session_player_from_player(player, db)

    # Get points and won games from session player
    total_points = session_player.points
    n_correct_answers = session_player.correct_answers
    denars = round_denars(total_points, DENAR_FACTOR)

    template_text = languages[get_lang_from_player_id(player_id, db)]

    result = {
        "request": request,
        "game_id": game_id,
        "total_points": total_points,
        "won_games": n_correct_answers,
        "text": template_text,
        "denars": denars,
        "player_id": player_id,
        "game_id": game_id,
    }

    return templates.TemplateResponse("games/end_of_session.html", result)


@router.get(
    "/{game_id}/player/{player_id}/thank_you",
    response_class=HTMLResponse,
)
def thank_you(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """
    Sends player to thank you page
    """
    template_text = languages[get_lang_from_player_id(player_id, db)]
    result = {
        "request": request,
        "text": template_text,
    }
    return templates.TemplateResponse("games/thanks_for_playing.html", result)


###########################################
# Utilities
###########################################


@router.get("/{game_id}", response_class=JSONResponse)
def route_game_access(
    game_id: int, db: Session = Depends(get_db)
) -> JSONResponse:
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    raise_exception_if_none(game, detail="game not found")
    return JSONResponse(
        content={
            "game_id": game_id,
            "rounds": game.rounds,
            "practice": game.practice,
        }
    )


@router.get("/{game_id}/player/{player_id}", response_class=JSONResponse)
def route_game_player_access(
    game_id: int, player_id: int, db: Session = Depends(get_db)
) -> JSONResponse:
    # tests to ensure game and player exists
    _, _ = get_game_and_player(game_id, player_id, db)

    return JSONResponse(content={"game_id": game_id, "player_id": player_id})


###########################################
# Unused
###########################################


@router.post("/{game_id}/player/{player_id}/ready")
def confirm_player(
    request: Request,
    player_id: int,
    game_id: int,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Confirms if the player is ready for the game
    """

    _, player = get_game_and_player(game_id, player_id, db)
    if not player.ready:
        player.ready = True
        db.commit()

    redirect_url = request.url_for(
        "get_qualtrics", game_id=game_id, player_id=player_id
    )

    return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)
