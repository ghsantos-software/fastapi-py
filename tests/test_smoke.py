from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_openapi_schema_ok():
    """A app sobe e expõe o schema OpenAPI."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "FastAPI"


def test_auth_home():
    """A rota pública de auth responde."""
    response = client.get("/auth/")
    assert response.status_code == 200
    assert response.json()["authenticate"] is False