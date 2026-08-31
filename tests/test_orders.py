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


def test_orders_route_requires_auth(client):
    response = client.get("/orders/")
    assert response.status_code == 401


def test_create_and_list_order(client):
    headers = _auth_headers(client)

    response = client.post("/orders/order", json={"user": 1}, headers=headers)
    assert response.status_code == 200
    assert "Order ID: 1" in response.json()["message"]

    response = client.get("/orders/list/orders-user", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["status"] == "PENDENT"