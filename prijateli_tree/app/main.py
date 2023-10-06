import os

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from prijateli_tree.app.controllers.administration import stuff
from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.getenv(KEY_DATABASE_URI))


@app.get("/")
def funky():
    return {"Hello": "World"}


@app.get("/administration")
def admin_access():
    stuff()
