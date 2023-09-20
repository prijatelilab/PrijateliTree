from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from models.config import config

from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


def create_application(config_name: str = "default"):
    fast_api_app = FastAPI()
    fast_api_app.config = config[config_name]

    fast_api_app.add_middleware(
        DBSessionMiddleware, db_url=fast_api_app.config[KEY_DATABASE_URI]
    )

    return fast_api_app


app = create_application()
