# backend/tests/test_cashboxes.py
from datetime import date
from starlette import status

LOGIN_URL = "/api/auth/login"
CASHBOXES_URL = "/api/cashboxes"


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


def _create_entry(client, headers: dict, cashbox_id: int, payload: dict):
    """
    Пробуем 2 варианта:
    A) POST /api/cashboxes/{cashbox_id}/entries
    B) POST /api/cashboxes/entries  (с cashbox_id в теле)
    """
    url_a = f"{CASHBOXES_URL}/{cashbox_id}/entries"
    res = client.post(url_a, json=payload, headers=headers)

    if res.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED):
        url_b = f"{CASHBOXES_URL}/entries"
        payload_b = {**payload, "cashbox_id": cashbox_id}
        res = client.post(url_b, json=payload_b, headers=headers)

    return res


def _update_entry(client, headers: dict, cashbox_id: int, entry_id: int, payload: dict):
    """
    Пробуем варианты:
    A) PATCH /api/cashboxes/entries/{id}
    B) PATCH /api/cashboxes/{cashbox_id}/entries/{id}
    C) PUT вместо PATCH (если нужно)
    """
    res = client.patch(f"{CASHBOXES_URL}/entries/{entry_id}", json=payload, headers=headers)

    if res.status_code == status.HTTP_404_NOT_FOUND:
        res = client.patch(
            f"{CASHBOXES_URL}/{cashbox_id}/entries/{entry_id}",
            json=payload,
            headers=headers,
        )

    if res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        res = client.put(f"{CASHBOXES_URL}/entries/{entry_id}", json=payload, headers=headers)

    return res


def test_cashboxes_list_exists_and_has_items(client, test_user, seed_cashbox):
    """
    seed_cashbox гарантирует, что в БД будет хотя бы 1 касса
    """
    headers = auth_headers(client, test_user)

    res = client.get(CASHBOXES_URL, headers=headers)
    assert res.status_code == 200, res.text
    items = _unwrap_list(res.json())

    assert isinstance(items, list), items
    assert len(items) >= 1, "Нужно хотя бы 1 касса в БД для теста"


def test_cashbox_entry_create_then_update_requires_reason(client, test_user, seed_cashbox):
    headers = auth_headers(client, test_user)

    # Берём кассу из фикстуры (не зависим от списка)
    cashbox_id = seed_cashbox.id

    # 2) Создаём запись
    create_payload = {
        "date": date.today().isoformat(),
        "amount_uzs": 10000,
        "comment": "pytest cashbox entry",
    }

    cr = _create_entry(client, headers, cashbox_id, create_payload)
    assert cr.status_code in (200, 201), f"Create failed: {cr.status_code} {cr.text}"

    created = cr.json() if cr.text else {}
    entry_id = created.get("id")

    # если id не вернулся — попробуем найти запись через список entries
    if not entry_id:
        list_url = f"{CASHBOXES_URL}/{cashbox_id}/entries"
        list_entries = client.get(list_url, headers=headers)
        assert list_entries.status_code == 200, list_entries.text
        entries = _unwrap_list(list_entries.json())
        hit = next((x for x in entries if (x.get("comment") or "") == "pytest cashbox entry"), None)
        assert hit and "id" in hit, entries
        entry_id = hit["id"]

    # 3) Попытка обновить БЕЗ edit_reason -> должно быть 400/422/403 (зависит от реализации)
    update_payload_no_reason = {
        "date": create_payload["date"],
        "amount_uzs": 20000,
        "comment": "pytest updated",
    }

    upd_a = _update_entry(client, headers, cashbox_id, entry_id, update_payload_no_reason)
    assert upd_a.status_code in (400, 401, 403, 422), (
        f"Expected error without reason, got {upd_a.status_code}: {upd_a.text}"
    )

    # 4) Обновляем С edit_reason -> должно пройти
    update_payload_with_reason = {
        "date": create_payload["date"],
        "amount_uzs": 25000,
        "comment": "pytest updated ok",
        "edit_reason": "pytest: fix",
    }

    upd_b = _update_entry(client, headers, cashbox_id, entry_id, update_payload_with_reason)
    assert upd_b.status_code in (200, 204), f"Update failed: {upd_b.status_code} {upd_b.text}"
