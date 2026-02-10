LOGIN_URL = "/api/auth/login"

def test_login_wrong_password(client):
    res = client.post(LOGIN_URL, json={
        "username": "test_admin",
        "password": "wrong"
    })
    assert res.status_code in (400, 401)


def test_login_success_returns_token(client, test_user):
    res = client.post(LOGIN_URL, json=test_user)

    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
