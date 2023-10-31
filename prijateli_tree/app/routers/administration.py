from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def admin_page():
    return {"message": "Admin getting schwifty"}
