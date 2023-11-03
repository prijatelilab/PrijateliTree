from datetime import datetime
from http import HTTPStatus
from typing import Annotated
from pathlib import Path

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from prijateli_tree.app.database import SessionLocal, User
from prijateli_tree.app.main import login_manager
from prijateli_tree.app.utils.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def admin_page(user=Depends(login_manager.optional)):
    if user is None:
        return RedirectResponse("admin_login", status_code=HTTPStatus.UNAUTHORIZED)
    return {"message": "Admin getting schwifty"}


@router.get("/login", response_class=HTMLResponse)
def admin_login():
    return templates.TemplateResponse("admin_login.html")


@router.post("/login")
def confirm_login(
    email: Annotated[str, Form()],
    birthdate_str: Annotated[str, Form()],
    db: Session = Depends(get_db),
):
    birthdate = datetime.strptime(birthdate_str, "%m/%d/%Y")
    user = (
        db.query(User)
        .filter_by(email=email.lower(), birthdate=birthdate)
        .filter(or_(User.role == ROLE_ADMIN, User.role == ROLE_SUPER_ADMIN))
        .one_or_none()
    )
    if user is None:
        raise InvalidCredentialsException

    access_token = login_manager.create_access_token(data={"sub": email})
    return {"access_token": access_token}
