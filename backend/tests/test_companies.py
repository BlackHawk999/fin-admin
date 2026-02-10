# backend/tests/test_companies.py
from starlette import status

LOGIN_URL = "/api/auth/login"
COMPANIES_URL = "/api/companies"


def get_token(client, username: str, password: str) -> str:
    res = client.post(LOGIN_URL, json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data, data
    return data["access_token"]


def auth_headers(client, test_user) -> dict:
    token = get_token(client, test_user["username"], test_user["password"])
    return {"Authorization": f"Bearer {token}"}


def unwrap_list(payload):
    # поддержка: [] или {"data": []}
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def test_companies_list_exists(client, test_user):
    headers = auth_headers(client, test_user)

    res = client.get(COMPANIES_URL, headers=headers)
    assert res.status_code == 200, res.text
    items = unwrap_list(res.json())
    assert isinstance(items, list), items


def test_company_create_then_update_then_get(client, test_user):
    headers = auth_headers(client, test_user)

    # 1) Create
    name = "pytest company"
    create_payload = {"name": name, "is_active": True}

    cr = client.post(COMPANIES_URL, json=create_payload, headers=headers)
    assert cr.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED), cr.text
    created = cr.json() if cr.text else {}
    company_id = created.get("id")

    # если id не вернулся — найдём по name через список
    if not company_id:
        ls = client.get(COMPANIES_URL, headers=headers)
        assert ls.status_code == 200, ls.text
        items = unwrap_list(ls.json())
        hit = next((x for x in items if (x.get("name") or "") == name), None)
        assert hit and "id" in hit, items
        company_id = hit["id"]

    # 2) Get detail (обычно /api/companies/{id})
    detail_url = f"{COMPANIES_URL}/{company_id}"
    gr = client.get(detail_url, headers=headers)
    # если detail endpoint нет — не валим тест, просто пропустим проверки detail
    if gr.status_code not in (status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED):
        assert gr.status_code == 200, gr.text

    # 3) Update (PATCH или PUT)
    upd_payload = {"name": "pytest company updated", "is_active": False}

    ur = client.patch(detail_url, json=upd_payload, headers=headers)
    if ur.status_code == 405:
        ur = client.put(detail_url, json=upd_payload, headers=headers)

    assert ur.status_code in (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT), ur.text

    # 4) Проверим что обновилось (если detail доступен)
    gr2 = client.get(detail_url, headers=headers)
    if gr2.status_code == 200 and gr2.text:
        obj = gr2.json()
        assert (obj.get("name") or "") == upd_payload["name"]
        assert bool(obj.get("is_active")) == upd_payload["is_active"]
    else:
        # fallback: проверим через список
        ls2 = client.get(COMPANIES_URL, headers=headers)
        assert ls2.status_code == 200, ls2.text
        items2 = unwrap_list(ls2.json())
        hit2 = next((x for x in items2 if x.get("id") == company_id), None)
        assert hit2 is not None, items2
        if "name" in hit2:
            assert hit2["name"] == upd_payload["name"]
        if "is_active" in hit2:
            assert bool(hit2["is_active"]) == upd_payload["is_active"]
