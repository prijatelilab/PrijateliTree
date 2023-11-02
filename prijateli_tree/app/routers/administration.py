from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from prijateli_tree.app.database import SessionLocal, User
from prijateli_tree.app.main import login_manager, templates
from prijateli_tree.app.utils.constants import ROLE_ADMIN, ROLE_SUPER_ADMIN


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.get("/")
def admin_page():
    return {"message": "Admin getting schwifty"}


@router.get("/login")
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
    if not user:
        raise InvalidCredentialsException

    access_token = login_manager.create_access_token(data={"sub": email})
    return {"access_token": access_token}
