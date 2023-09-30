import os

from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware

from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


app = FastAPI()
print(os.getenv(KEY_DATABASE_URI))

app.add_middleware(DBSessionMiddleware, db_url=os.getenv(KEY_DATABASE_URI))


@app.get("/")
def funky():
    return {"Hello": "World"}
