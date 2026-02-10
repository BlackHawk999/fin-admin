from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings

# ВАЖНО:
# Если ты используешь Alembic, НЕ нужно делать Base.metadata.create_all().
# Таблицы должны создаваться через миграции: alembic upgrade head
#
# Импорты моделей в main.py тоже не обязательны, если Alembic env.py импортирует app.models.
# Но если где-то в проекте это нужно для регистрации моделей — можно оставить.
from .models import user, employee, company, cashbox, owner, expense  # noqa: F401

from .routers import auth, employees, companies, cashboxes, owners, expenses, exports, dashboard

app = FastAPI(
    title="Fin Admin API",
    description="Financial accounting admin panel API",
    version="0.1.0",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(cashboxes.router, prefix="/api")
app.include_router(owners.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Fin Admin API", "docs": "/docs"}
