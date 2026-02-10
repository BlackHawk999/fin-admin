# backend/tests/test_workers.py
from datetime import date
from starlette import status

LOGIN_URL = "/api/auth/login"


def get_token(client, username: str, password: str) -> str:
    res = client.post(LOGIN_URL, json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data, data
    return data["access_token"]


def auth_headers(client, test_user) -> dict:
    token = get_token(client, test_user["username"], test_user["password"])
    return {"Authorization": f"Bearer {token}"}


def pick_workers_base_url(client, headers) -> str:
    """
    Подбираем правильный base url:
    - /api/workers
    - /api/employees
    """
    for base in ("/api/workers", "/api/employees"):
        r = client.get(base, headers=headers)
        if r.status_code != 404:
            return base
    raise AssertionError("Не найден workers endpoint: нет ни /api/workers ни /api/employees (оба дают 404)")


def unwrap_list(payload):
    # поддержка: [] или {"data": []}
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def test_workers_list_exists(client, test_user):
    headers = auth_headers(client, test_user)
    base = pick_workers_base_url(client, headers)

    res = client.get(base, headers=headers)
    assert res.status_code == 200, res.text
    items = unwrap_list(res.json())
    assert isinstance(items, list), items


def test_worker_create_then_update_then_get(client, test_user):
    headers = auth_headers(client, test_user)
    base = pick_workers_base_url(client, headers)

    # 1) Create
    payload = {
        "full_name": "pytest worker",
        "monthly_salary_uzs": 123456,
        "is_active": True,
    }

    cr = client.post(base, json=payload, headers=headers)
    assert cr.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED), cr.text
    created = cr.json() if cr.text else {}
    worker_id = created.get("id")

    # если id не вернулся — попробуем найти по имени
    if not worker_id:
        ls = client.get(base, headers=headers)
        assert ls.status_code == 200, ls.text
        items = unwrap_list(ls.json())
        hit = next((x for x in items if (x.get("full_name") or "") == payload["full_name"]), None)
        assert hit and "id" in hit, items
        worker_id = hit["id"]

    # 2) Get detail (варианты: /{id})
    detail_url = f"{base}/{worker_id}"
    gr = client.get(detail_url, headers=headers)
    assert gr.status_code == 200, gr.text

    # 3) Update (PATCH или PUT)
    upd_payload = {
        "full_name": "pytest worker updated",
        "monthly_salary_uzs": 777777,
        "is_active": False,
    }

    ur = client.patch(detail_url, json=upd_payload, headers=headers)
    if ur.status_code == 405:
        ur = client.put(detail_url, json=upd_payload, headers=headers)

    assert ur.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT), ur.text

    # 4) Get again and verify updated fields (если API возвращает объект)
    gr2 = client.get(detail_url, headers=headers)
    assert gr2.status_code == 200, gr2.text
    obj = gr2.json()

    # Эти поля должны совпасть если endpoint detail отдаёт модель
    assert (obj.get("full_name") or "") == upd_payload["full_name"]
    assert int(obj.get("monthly_salary_uzs") or 0) == upd_payload["monthly_salary_uzs"]
    assert bool(obj.get("is_active")) == upd_payload["is_active"]
