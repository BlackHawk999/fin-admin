# Fin Admin — админ-панель финансового учёта магазина

MVP админ-панели для учёта: работники (зарплаты/авансы), фирмы, кассы, расходы и владельцы.

## Стек

- **Frontend:** Vue 3, TypeScript, Vite, Vue Router, Pinia, Axios, Chart.js, SCSS (БЭМ)
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Alembic, PostgreSQL, JWT
- **Деплой:** Render (Backend — Web Service, Frontend — Static Site)

## Структура проекта

```
fin-admin/
├── backend/                 # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   ├── models/
│   │   ├── schemas/
│   │   └── routers/
│   ├── alembic/
│   ├── scripts/
│   │   └── init_db.py       # создание admin + 4 касс
│   ├── requirements.txt
│   ├── runtime.txt          # Python 3.11.9
│   └── .env.example
├── frontend/                # Vue 3 + Vite
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── router/
│   │   └── styles/
│   ├── package.json
│   └── .env.example
└── README.md
```

## Локальный запуск

### 1. PostgreSQL

Убедитесь, что PostgreSQL запущен и создана БД, например:

```bash
createdb finadmin
```

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env: DATABASE_URL и SECRET_KEY
```

Применить миграции и создать пользователя + кассы:

```bash
alembic upgrade head
python -m scripts.init_db
```

Запуск API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Документация: http://localhost:8000/docs

Логин по умолчанию после `init_db`: **admin** / **admin** (если не заданы `ADMIN_USERNAME` / `ADMIN_PASSWORD` в `.env`).

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Для локальной разработки VITE_API_URL можно оставить пустым (прокси в vite.config на :8000)
npm run dev
```

Фронт: http://localhost:5173

## Деплой на Render

### Версия Python

- В проекте зафиксирована **Python 3.11.9** в `backend/runtime.txt` и `backend/.python-version`.
- На Render в настройках Web Service укажите ту же версию или оставьте авто (Render прочитает `runtime.txt`).

### Backend (Web Service)

1. **New → Web Service**
2. Подключите репозиторий (GitHub/GitLab).
3. Настройки:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build Command:**  
     `pip install -r requirements.txt`
   - **Start Command:**  
     `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment:**
   - `DATABASE_URL` — возьмите из **Render Postgres** (Internal URL). Если в значении указано `postgres://`, приложение автоматически заменит на `postgresql://`.
   - `SECRET_KEY` — сгенерируйте надёжный ключ (например: `openssl rand -hex 32`).
   - При необходимости: `CORS_ORIGINS` = `https://ваш-frontend.onrender.com`
5. После первого деплоя выполните миграции и инициализацию БД (в **Shell** или одноразовый job):
   - `alembic upgrade head`
   - `python -m scripts.init_db`
   Либо добавьте в **Start Command**:  
   `alembic upgrade head && python -m scripts.init_db && uvicorn app.main:app --host 0.0.0.0 --port $PORT`  
   (только для первого запуска; потом лучше убрать `init_db` из старта.)

### База данных (Postgres)

1. **New → PostgreSQL** и создайте БД.
2. В настройках сервиса скопируйте **Internal Database URL** в переменную `DATABASE_URL` бэкенда.

### Frontend (Static Site)

1. **New → Static Site**
2. Подключите тот же репозиторий.
3. Настройки:
   - **Root Directory:** `frontend`
   - **Build Command:**  
     `npm install && npm run build`
   - **Publish Directory:** `dist`
4. **Environment:**
   - `VITE_API_URL` = `https://ваш-backend.onrender.com/api`  
     (URL вашего Web Service + `/api`)

После деплоя статики откройте сайт и проверьте логин и запросы к API.

## Функции MVP

- **Работники:** список, добавление, зарплата; страница работника — авансы за период, остаток к выдаче.
- **Фирмы:** список, операции (IN/OUT), баланс за период.
- **Кассы:** 4 кассы (2 дневные, 2 ночные), записи по датам, итоги за период.
- **Расходы:** таблица с фильтрами по дате, категории, владельцу; владельцы с цветами; экспорт в Excel по выбранным фильтрам.
- **Главная:** расходы за сегодня, последние расходы, графики по дням и по категориям за 30 дней.
- **Владельцы:** справочник имён и цветов (HEX).

Экспорт расходов: кнопка «Скачать Excel» на странице Расходы, файл `expenses_YYYY-MM-DD_to_YYYY-MM-DD.xlsx` с учётом активных фильтров.

## Лицензия

MIT
