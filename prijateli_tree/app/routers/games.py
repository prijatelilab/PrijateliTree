import glob
import json
from collections import Counter
from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.datastructures import URL

from prijateli_tree.app.database import (
    Game,
    GameAnswer,
    GamePlayer,
    GameSession,
    GameSessionPlayer,
    SessionLocal,
)
from prijateli_tree.app.utils.constants import (
    BALL_BLUE,
    BALL_RED,
    DENIR_FACTOR,
    FILE_MODE_READ,
    STANDARD_ENCODING,
    WINNING_SCORE,
)
from prijateli_tree.app.utils.games import Game as GameUtil


router = APIRouter()


def raise_exception_if_none(x, detail):
    if x is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=detail)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))

languages = {}
for lang in glob.glob("prijateli_tree/app/languages/*.json"):
    with open(lang, FILE_MODE_READ, encoding=STANDARD_ENCODING) as file:
        languages.update(json.load(file))


def get_bag_color(bag):
    """
    Gets color of the bag based on the number of red and blue balls
    """
    # Check if bag is red or blue
    balls_counter = Counter(bag)
    correct_answer = False
    if balls_counter[BALL_RED] > balls_counter[BALL_BLUE]:
        correct_answer = BALL_RED
    elif balls_counter[BALL_RED] < balls_counter[BALL_BLUE]:
        correct_answer = BALL_BLUE

    return correct_answer


def get_current_round(game_id: int, db: Session = Depends(get_db)) -> int:
    """
    Gets the game's current round given the game id
    """
    players = db.query(GamePlayer).filter_by(game_id=game_id).all()
    n_answers = 0

    for player in players:
        n_answers += len(player.answers)

    current_round = n_answers // len(players) + 1

    return current_round


def get_game_and_player(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    """
    Helper function to ensure game and player exist
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()

    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    filtered_player = [p for p in game.players if p.id == player_id]

    if not len(filtered_player):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not in game"
        )
    return game, filtered_player[0]


def get_game_and_type(game_id: int, db: Session = Depends(get_db)):
    """
    Helper function to ensure game and game type exist
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()

    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    return game, game.game_type


def get_lang_from_player_id(player_id: int, db: Depends(get_db)):
    """
    Get language from player_id
    """
    player = db.query(GamePlayer).filter_by(id=player_id).one_or_none()

    if player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not found"
        )

    return player.language.abbr


def did_player_win(
    game: Game,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Helper function that determines if the player won,
    the color of the bag and their guess
    """

    # Check if bag is red or blue
    correct_color = get_bag_color(game.game_type.bag)

    # Get the player's previous answer
    latest_guess = get_previous_answers(game.id, player_id, db)
    player_guess = latest_guess["your_previous_answer"]

    return {
        "correct_color": correct_color,
        "player_guess": player_guess,
        "is_correct": player_guess == correct_color,
    }


def get_previous_answers(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that returns the player's previous answer
    from the last round, along with the answers of their neighbors
    """
    game, player = get_game_and_player(game_id, player_id, db)

    # Get current round
    current_round = get_current_round(game_id, db)

    if current_round == 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="no previous answers"
        )
    else:
        last_round = current_round - 1

    player_answer = [a for a in player.answers if a.round == last_round][0]

    # Use game utils to get the player's neighbors
    game_util = GameUtil(game.game_type.network)
    neighbors_positions = game_util.neighbors[player.position]

    neighbors_answers = []
    neighbors_names = []
    # Get the neighbors' previous answers
    for neighbor_position in neighbors_positions:
        this_neighbor = (
            db.query(GamePlayer)
            .filter_by(game_id=game_id, position=neighbor_position)
            .one_or_none()
        )
        this_answer = [
            a for a in this_neighbor.answers if a.round == last_round
        ][0]

        # Check if names are hidden
        if game.game_type.names_hidden:
            player_id = this_neighbor.user.id
            complete_name = f"Player {player.position}: "
        else:
            complete_name = f"{this_neighbor.user.first_name} {this_neighbor.user.last_name}: "

        neighbors_names.append(complete_name)
        neighbors_answers.append(this_answer.player_answer)

    return {
        "your_previous_answer": player_answer.player_answer,
        "neighbors_previous_answer": neighbors_answers,
        "neighbors_names": neighbors_names,
    }


###############################
#
#        BEGIN API
#
###############################


@router.get("/session/{session_id}")
def route_session_access(
    request: Request, session_id: int, db: Session = Depends(get_db)
):
    # Do some logic things
    session = db.query(GameSession).filter_by(id=session_id).one_or_none()

    raise_exception_if_none(session, "session not found")

    return templates.TemplateResponse(
        "new_session.html", context={"request": request}
    )


@router.get("/{game_id}")
def route_game_access(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )
    return {
        "game_id": game_id,
        "rounds": game.rounds,
        "practice": game.practice,
    }


@router.get("/{game_id}/player/{player_id}")
def route_game_player_access(
    game_id: int, player_id: int, db: Session = Depends(get_db)
):
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    if len([player for player in game.players if player.id == player_id]) != 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="player not found in game"
        )

    return {"game_id": game_id, "player_id": player_id}


@router.post("/{game_id}/player/{player_id}/answer")
def route_add_answer(
    game_id: int,
    player_id: int,
    player_answer: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Function that updates the player's guess in the database
    """
    game = db.query(Game).filter_by(id=game_id).one_or_none()
    if game is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="game not found"
        )

    # Getting correct answer and current round
    correct_answer = get_bag_color(game.game_type.bag)
    current_round = get_current_round(game_id, db)

    if (
        db.query(GameAnswer)
        .filter_by(game_player_id=player_id, round=current_round)
        .one_or_none()
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="answer already exists for player and round",
        )

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

    redirect_url = f"/games/{game_id}/player/{player_id}/waiting"

    return RedirectResponse(url=redirect_url, status_code=HTTPStatus.SEE_OTHER)


@router.get("/{game_id}/player/{player_id}/round")
def view_round(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that returns the current round
    """
    game, player = get_game_and_player(game_id, player_id, db)

    template_text = languages[player.language.abbr]
    current_round = get_current_round(game_id, db)
    template_data = {
        "first_round": current_round == 1,
        "current_round": current_round,
        "text": template_text,
        "player_id": player_id,
        "game_id": game_id,
    }
    # Get current round
    if current_round == 1:
        template_data["ball"] = player.initial_ball
    else:
        template_data["previous_answers"] = get_previous_answers(
            game_id, player_id, db
        )

    return templates.TemplateResponse(
        "round.html", {"request": request, **template_data}
    )


@router.get("/{game_id}/all_set")
def all_set(
    request: Request,
    game_id: int,
    db: Session = Depends(get_db),
):
    """
    Determines if all players have submitted a guess in the current round
    """
    players = db.query(GamePlayer).filter_by(game_id=game_id).all()
    n_answers = 0
    for player in players:
        n_answers += len(player.answers)

    ready = n_answers % len(players) == 0

    return {"ready": ready}


@router.get("/{game_id}/player/{player_id}/waiting")
def waiting(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Wait screen shows until all players are ready to move to the next section
    """
    template_text = languages[get_lang_from_player_id(player_id, db)]

    result = {
        "request": request,
        "game_id": game_id,
        "player_id": player_id,
        "text": template_text,
    }

    return templates.TemplateResponse("waiting.html", result)


def get_session_player_from_player(
    player: GamePlayer, db: Session = Depends(get_db)
):
    session_player = (
        db.query(GameSessionPlayer)
        .filter_by(id=player.session_player_id)
        .one_or_none()
    )

    if session_player is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="GameSessionPlayer not found",
        )
    return session_player


@router.put("/{game_id}/player/{player_id}/update_score")
def route_add_score(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that updates the player's score in the database
    """
    game, player = get_game_and_player(game_id, player_id, db)
    game_status = did_player_win(game, player_id, db)
    session_player = get_session_player_from_player(player, db)

    session_player.correct_answers += game_status["is_correct"]
    session_player.points += game_status["is_correct"] * WINNING_SCORE
    db.commit()
    db.refresh(session_player)

    redirect_url = URL("games/{game_id}/player/{player_id}/end_of_game")

    return RedirectResponse(url=redirect_url, status_code=HTTPStatus.FOUND)


@router.get("/current_score/{player_id}")
def route_get_score(
    request: Request,
    player_id: int,
    db: Session = Depends(get_db),
):
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
    return session_player.points


@router.get("/{game_id}/player/{player_id}/end_of_game")
def route_end_of_game(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that returns the end of game page and
    template.
    """

    game, player = get_game_and_player(game_id, player_id, db)
    game_status = did_player_win(game, player_id, db)

    points = 0
    if game_status["is_correct"]:
        points = WINNING_SCORE

    template_text = languages[player.language.abbr]

    result = {
        "request": request,
        "player_id": player_id,
        "game_id": game_id,
        "points": points,
        "text": template_text,
    }

    # add information about winning and ball colors
    result.update(game_status)

    return templates.TemplateResponse("end_of_game.html", result)


@router.get("/{game_id}/player/{player_id}/start_of_game")
def view_start_of_game(
    request: Request,
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that returns the end of game page and
    template.
    """

    template_text = languages[get_lang_from_player_id(player_id, db)]

    result = {
        "request": request,
        "player_id": player_id,
        "game_id": game_id,
        "points": WINNING_SCORE,
        "text": template_text,
    }

    return templates.TemplateResponse("start_of_game.html", result)


@router.post("/{game_id}/player/{player_id}/denirs")
def score_to_denirs(
    game_id: int,
    player_id: int,
    db: Session = Depends(get_db),
):
    """
    Function that calculates the denirs for the player
    given all of their scores
    """
    total_score = 0
    game, player = get_game_and_player(game_id, player_id, db)

    for answer in player.answers:
        if answer.player_answer == answer.correct_answer:
            total_score += WINNING_SCORE

    denirs = total_score * DENIR_FACTOR

    return {"reward": f"You have made {denirs} denirs!"}


@router.post("/ready")
def confirm_player(
    player_id: int,
    game_id: int,
    db: Session = Depends(get_db),
):
    """
    Confirms if the player is ready for the game
    """

    game, player = get_game_and_player(game_id, player_id, db)

    player.ready = True
    db.commit()

    return {"status": "Player is ready!"}


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
        # TODO: end of session screen
        return

    next_player_id = (
        db.query(GamePlayer)
        .filter_by(user_id=player.user_id, game_id=game.next_game_id)
        .one()
        .id
    )
    # game.next_game_id
    # next_player_id
    redirect_url = request.url_for(
        "view_start_of_game",
        game_id=game.next_game_id,
        player_id=next_player_id,
    )

    return RedirectResponse(
        redirect_url,
        status_code=HTTPStatus.FOUND,
    )
