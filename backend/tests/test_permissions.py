# backend/tests/test_permissions.py
from starlette import status
import pytest
from datetime import date

LOGIN_URL = "/api/auth/login"
CASHBOXES_URL = "/api/cashboxes"
EXPENSES_URL = "/api/expenses"


def login(client, username, password):
    res = client.post(LOGIN_URL, json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_non_admin_cannot_create_cashbox(client, test_user):
    """
    Если POST /cashboxes не существует -> SKIP
    Если существует -> user должен получить 401/403
    """
    token = login(client, test_user["username"], test_user["password"])
    headers = auth_headers(token)

    payload = {"name": "pytest forbidden cashbox", "currency": "UZS"}
    res = client.post(CASHBOXES_URL, json=payload, headers=headers)

    if res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        pytest.skip("POST /api/cashboxes не реализован -> тест ролей тут невозможен")
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), res.text


def test_protected_without_token_returns_401_or_403(client):
    """
    Любой protected endpoint должен ругаться без токена.
    """
    res = client.get(CASHBOXES_URL)
    assert res.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), res.text


def test_non_admin_cannot_delete_expense(client, test_user):
    """
    Если delete expense существует и защищён ролями -> user должен получить 401/403.
    Если delete не существует -> SKIP.
    """
    token = login(client, test_user["username"], test_user["password"])
    headers = auth_headers(token)

    create_payload = {
        "date": date.today().isoformat(),
        "amount_uzs": 1111,
        "category": "pytest",
        "comment": "forbidden delete test",
        "payer_type": "other",
        "owner_id": None,
    }

    cr = client.post(EXPENSES_URL, json=create_payload, headers=headers)
    if cr.status_code in (401, 403):
        pytest.skip("Создание расхода тоже запрещено для user -> роли уже работают, но этот тест не актуален")
    if cr.status_code == 405:
        pytest.skip("POST /api/expenses не реализован")

    expense_id = cr.json().get("id")
    assert expense_id, cr.text

    dr = client.delete(f"{EXPENSES_URL}/{expense_id}", headers=headers)

    if dr.status_code == 405:
        pytest.skip("DELETE /api/expenses/{id} не реализован -> тест ролей тут невозможен")

    assert dr.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN), dr.text
