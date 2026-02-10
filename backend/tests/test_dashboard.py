# backend/tests/test_dashboard.py
from datetime import date, timedelta
from starlette import status

LOGIN_URL = "/api/auth/login"
SUMMARY_URL = "/api/dashboard/summary"
BY_DAY_URL = "/api/expenses/by-day"
EXPENSES_URL = "/api/expenses"

# Кандидаты для экспорта (часто встречающиеся варианты)
EXPORT_CANDIDATES = [
    # GET варианты
    ("GET", "/api/exports/expenses"),
    ("GET", "/api/exports/expenses-excel"),
    ("GET", "/api/exports/expenses_excel"),
    ("GET", "/api/exports/expenses/xlsx"),
    ("GET", "/api/exports/expenses.xlsx"),
    ("GET", "/api/exports/expensesExcel"),
    ("GET", "/api/exports/expenses/excel"),
    # POST варианты (если экспорт сделан POST'ом)
    ("POST", "/api/exports/expenses"),
    ("POST", "/api/exports/expenses-excel"),
    ("POST", "/api/exports/expenses_excel"),
    ("POST", "/api/exports/expenses/excel"),
]


def get_token(client, username: str, password: str) -> str:
    res = client.post(LOGIN_URL, json={"username": username, "password": password})
    assert res.status_code == 200, res.text
    data = res.json()
    assert "access_token" in data, data
    return data["access_token"]


def auth_headers(client, test_user) -> dict:
    token = get_token(client, test_user["username"], test_user["password"])
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_summary_structure(client, test_user):
    headers = auth_headers(client, test_user)

    res = client.get(SUMMARY_URL, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()

    required_keys = [
        "expenses_today_uzs",
        "expenses_this_month_uzs",
        "cashboxes_today_total_uzs",
        "companies_out_this_month_uzs",
    ]

    for key in required_keys:
        assert key in data, data
        assert isinstance(data[key], (int, float)), (key, data[key])


def test_expenses_by_day_returns_list(client, test_user):
    headers = auth_headers(client, test_user)

    date_to = date.today()
    date_from = date_to - timedelta(days=6)

    res = client.get(
        BY_DAY_URL,
        params={"date_from": date_from.isoformat(), "date_to": date_to.isoformat()},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    payload = res.json()
    assert isinstance(payload, list), payload

    if payload:
        item = payload[0]
        assert "date" in item and "total_uzs" in item, item
        assert isinstance(item["date"], str)
        assert isinstance(item["total_uzs"], (int, float))


def test_last_expenses_limit_10(client, test_user):
    headers = auth_headers(client, test_user)

    res = client.get(EXPENSES_URL, params={"limit": 10}, headers=headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert isinstance(data, list), data
    assert len(data) <= 10, len(data)


def _looks_like_file_response(res) -> bool:
    ct = (res.headers.get("content-type") or "").lower()
    disp = (res.headers.get("content-disposition") or "").lower()

    # excel часто приходит как:
    # - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    # - application/octet-stream
    # + content-disposition: attachment; filename=...
    if "spreadsheetml" in ct:
        return True
    if "octet-stream" in ct and len(res.content) > 100:
        return True
    if "attachment" in disp and len(res.content) > 100:
        return True
    return False


def test_export_excel_returns_file(client, test_user):
    headers = auth_headers(client, test_user)

    today = date.today().isoformat()
    params = {"date_from": today, "date_to": today}

    last_error = None

    for method, url in EXPORT_CANDIDATES:
        if method == "GET":
            res = client.get(url, params=params, headers=headers)
        else:
            res = client.post(url, json=params, headers=headers)

        if res.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED):
            last_error = (method, url, res.status_code, res.text)
            continue

        assert res.status_code == 200, f"{method} {url} -> {res.status_code}: {res.text}"
        assert _looks_like_file_response(res), (
            f"{method} {url} не похож на файл. content-type={res.headers.get('content-type')}"
        )
        assert len(res.content) > 100, "Похоже пришёл пустой файл"
        return

    assert False, f"Не нашли рабочий endpoint экспорта. Последняя ошибка: {last_error}"
