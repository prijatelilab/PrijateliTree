import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)


def create_application():
    fast_api_app = FastAPI()

    fast_api_app.add_middleware(DBSessionMiddleware, db_url=os.getenv(KEY_DATABASE_URI))

    return fast_api_app


app = create_application()


@app.get("/")
def funky():
    return {"Hello": "World"}
