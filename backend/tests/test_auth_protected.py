# backend/tests/test_auth_protected.py
from starlette import status

LOGIN_URL = "/api/auth/login"
ME_URL = "/api/cashboxes"  # 👈 если у тебя именно так, если нет — скажи

def get_token(client, username: str, password: str) -> str:
    res = client.post(
        LOGIN_URL,
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text

    data = res.json()
    assert "access_token" in data, data
    return data["access_token"]


def test_protected_without_token_returns_401(client):
    res = client.get(ME_URL)
    assert res.status_code in (
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ), res.text


def test_protected_with_token_returns_200(client, test_user):
    token = get_token(client, test_user["username"], test_user["password"])

    res = client.get(
        ME_URL,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
