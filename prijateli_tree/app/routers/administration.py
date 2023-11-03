from pathlib import Path

from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from prijateli_tree.app.database import SessionLocal


router = APIRouter()

base_dir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(base_dir, "../templates")))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def admin_page():
    return {"message": "Admin getting schwifty"}
