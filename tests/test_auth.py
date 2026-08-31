def _create_account(client, email="a@a.com", password="123456"):
    return client.post(
        "/auth/create_account",
        json={"name": "Test", "email": email, "password": password},
    )


def test_create_account_ok(client):
    response = _create_account(client)
    assert response.status_code == 200
    assert "a@a.com" in response.json()["message"]


def test_create_account_duplicate_email(client):
    _create_account(client)
    response = _create_account(client)
    assert response.status_code == 400


def test_login_returns_token(client):
    _create_account(client)
    response = client.post(
        "/auth/login", json={"email": "a@a.com", "password": "123456"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["access token"]


def test_login_wrong_password(client):
    _create_account(client)
    response = client.post(
        "/auth/login", json={"email": "a@a.com", "password": "wrong"}
    )
    assert response.status_code == 400


def test_login_unknown_user(client):
    response = client.post(
        "/auth/login", json={"email": "nobody@x.com", "password": "x"}
    )
    assert response.status_code == 400