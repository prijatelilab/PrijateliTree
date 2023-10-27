from fastapi import APIRouter

from prijateli_tree.app.database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def admin_page():
    return {"message": "Admin getting schwifty"}
