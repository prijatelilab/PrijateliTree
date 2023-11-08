import os
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.orm import Session

from prijateli_tree.app.database import SessionLocal, User
from prijateli_tree.app.utils.constants import (
    KEY_LOGIN_SECRET,
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
)


base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))


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
        return RedirectResponse(
            "login", status_code=HTTPStatus.FOUND
        )
    else:
        return RedirectResponse("dashboard", status_code=HTTPStatus.FOUND)


@router.get("/login", response_class=HTMLResponse)
def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.post("/login")
def confirm_login(
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
        raise InvalidCredentialsException

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
    request: Request, user=Depends(login_manager), db: Session = Depends(get_db)
):
    return templates.TemplateResponse(
        "admin_dashboard.html", {"request": request, "user": user}
    )
