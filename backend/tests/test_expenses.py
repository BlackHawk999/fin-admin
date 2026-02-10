# backend/tests/test_expenses.py
from datetime import date
from starlette import status

LOGIN_URL = "/api/auth/login"
EXPENSES_URL = "/api/expenses"
OWNERS_URL = "/api/owners"


def get_token(client, username: str, password: str) -> str:
    res = client.post(LOGIN_URL, json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data, data
    return data["access_token"]


def auth_headers(client, test_user) -> dict:
    token = get_token(client, test_user["username"], test_user["password"])
    return {"Authorization": f"Bearer {token}"}


def _unwrap_list(payload):
    # поддержка: [] или {"data": []}
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def _pick_owner_id_if_exists(client, headers) -> int | None:
    """Если owners есть — вернём первого. Если нет — None."""
    r = client.get(OWNERS_URL, headers=headers)
    if r.status_code != 200:
        return None
    items = _unwrap_list(r.json())
    if isinstance(items, list) and items:
        return items[0].get("id")
    return None


def test_expenses_list_works(client, test_user):
    headers = auth_headers(client, test_user)
    r = client.get(EXPENSES_URL, headers=headers)
    assert r.status_code == 200, r.text
    items = _unwrap_list(r.json())
    assert isinstance(items, list), items


def test_expenses_create_update_delete_flow(client, test_user):
    headers = auth_headers(client, test_user)

    owner_id = _pick_owner_id_if_exists(client, headers)

    # 1) CREATE (payer_type=other)
    create_payload = {
        "date": date.today().isoformat(),
        "amount_uzs": 12345,
        "category": "pytest category",
        "comment": "pytest expense",
        "payer_type": "other",
        "owner_id": None,
    }

    cr = client.post(EXPENSES_URL, json=create_payload, headers=headers)
    assert cr.status_code in (200, 201), cr.text

    created = cr.json() if cr.text else {}
    expense_id = created.get("id")

    # если id не вернулся — попробуем найти по comment
    if not expense_id:
        lr = client.get(EXPENSES_URL, headers=headers)
        assert lr.status_code == 200, lr.text
        items = _unwrap_list(lr.json())
        hit = next((x for x in items if (x.get("comment") or "") == "pytest expense"), None)
        assert hit and "id" in hit, items
        expense_id = hit["id"]

    # 2) UPDATE (поменяем сумму/коммент, и попробуем payer_type=owner если есть owner)
    update_payload = {
        "date": create_payload["date"],
        "amount_uzs": 77777,
        "category": "pytest category upd",
        "comment": "pytest expense updated",
        "payer_type": "owner" if owner_id else "other",
        "owner_id": owner_id if owner_id else None,
    }

    # PATCH или PUT — пробуем PATCH, если 405 -> PUT
    ur = client.patch(f"{EXPENSES_URL}/{expense_id}", json=update_payload, headers=headers)
    if ur.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        ur = client.put(f"{EXPENSES_URL}/{expense_id}", json=update_payload, headers=headers)

    assert ur.status_code in (200, 204), ur.text

    # 3) GET list and ensure updated comment exists
    lr2 = client.get(EXPENSES_URL, headers=headers)
    assert lr2.status_code == 200, lr2.text
    items2 = _unwrap_list(lr2.json())
    assert any((x.get("comment") or "") == "pytest expense updated" for x in items2), items2

    # 4) DELETE
    dr = client.delete(f"{EXPENSES_URL}/{expense_id}", headers=headers)
    assert dr.status_code in (200, 204), dr.text

    # 5) Ensure removed (если API реально удаляет)
    lr3 = client.get(EXPENSES_URL, headers=headers)
    assert lr3.status_code == 200, lr3.text
    items3 = _unwrap_list(lr3.json())
    assert not any(x.get("id") == expense_id for x in items3), items3
