from fastapi import APIRouter

from prijateli_tree.app.database import SessionLocal


router = APIRouter()


@router.get("/")
def admin_page():
    return {"message": "Admin getting schwifty"}
