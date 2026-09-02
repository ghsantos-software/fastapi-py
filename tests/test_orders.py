def _auth_headers(client, email="o@o.com"):
    client.post(
        "/auth/create_account",
        json={"name": "Owner", "email": email, "password": "123456"},
    )
    response = client.post(
        "/auth/login", json={"email": email, "password": "123456"}
    )
    token = response.json()["access token"]
    return {"Authorization": f"Bearer {token}"}


def _create_order(client, headers):
    response = client.post("/orders/order", json={"user": 1}, headers=headers)
    assert response.status_code == 200
    return response


def test_orders_route_requires_auth(client):
    response = client.get("/orders/")
    assert response.status_code == 401


def test_create_and_list_order(client):
    headers = _auth_headers(client)

    _create_order(client, headers)

    response = client.get("/orders/list/orders-user", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "PENDENT"


def test_login_form_returns_token(client):
    """A rota que o botão 'Authorize' do /docs usa precisa funcionar."""
    client.post(
        "/auth/create_account",
        json={"name": "Owner", "email": "form@f.com", "password": "123456"},
    )
    response = client.post(
        "/auth/login-form",
        data={"username": "form@f.com", "password": "123456"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "Bearer"
    assert body["access token"]


def test_cancel_order(client):
    headers = _auth_headers(client)
    _create_order(client, headers)

    response = client.post("/orders/order/cancel/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELED"


def test_finish_order(client):
    headers = _auth_headers(client)
    _create_order(client, headers)

    response = client.post("/orders/order/finish/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_add_item_updates_price_and_view_order(client):
    headers = _auth_headers(client)
    _create_order(client, headers)

    response = client.post(
        "/orders/order/add-item/1",
        json={"amount": 3, "taste": "mint", "size": "M", "unit_price": 5.0},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["price"] == 15.0

    response = client.get("/orders/order/1", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["amount_items_order"] == 1
    assert body["order"]["price"] == 15.0
    assert body["order"]["items"][0]["amount"] == 3


def test_remove_item_recalculates_price(client):
    headers = _auth_headers(client)
    _create_order(client, headers)
    client.post(
        "/orders/order/add-item/1",
        json={"amount": 2, "taste": "vanilla", "size": "L", "unit_price": 4.0},
        headers=headers,
    )

    response = client.post("/orders/order/remove_item/1", headers=headers)
    assert response.status_code == 200
    assert response.json()["price"] == 0


def test_remove_missing_item_returns_400(client):
    headers = _auth_headers(client)

    response = client.post("/orders/order/remove_item/999", headers=headers)
    assert response.status_code == 400


def test_view_missing_order_returns_400(client):
    headers = _auth_headers(client)

    response = client.get("/orders/order/999", headers=headers)
    assert response.status_code == 400