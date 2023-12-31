import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from prijateli_tree.app.main import app
from prijateli_tree.app.utils.constants import KEY_DATABASE_URI


@pytest.fixture(name="session")
def session_fixture():
    print(os.getenv(KEY_DATABASE_URI))
    engine = create_engine(
        os.getenv(KEY_DATABASE_URI),
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        add_mockdata(session)
        yield session


def add_mockdata(session: Session):
    # Add data you want to the test DB using the `session` object.
    pass


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides["get_session"] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
