from http import HTTPStatus

from fastapi.testclient import TestClient


def test_home_page(client: TestClient):
    """Test home page functionality."""
    response = client.get("/")

    assert "Welcome to the PrijateliTree application!" in response.text
    assert response.status_code == HTTPStatus.OK
