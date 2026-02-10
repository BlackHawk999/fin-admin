# backend/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient

# 1) ENV ДОЛЖЕН БЫТЬ ДО ИМПОРТА app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")

from app.main import app  # noqa: E402
from app.database import Base, engine, SessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.cashbox import Cashbox  # noqa: E402
from app.auth import get_password_hash  # noqa: E402


# -------------------- CLIENT --------------------
@pytest.fixture(scope="function")
def client():
    # CI всегда стартует с пустой БД
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c


# -------------------- USER --------------------
@pytest.fixture(scope="function")
def test_user():
    db = SessionLocal()

    user = db.query(User).filter(User.username == "test_admin").first()
    if not user:
        user = User(
            username="test_admin",
            hashed_password=get_password_hash("test123"),
        )
        db.add(user)
        db.commit()

    db.close()
    return {
        "username": "test_admin",
        "password": "test123",
    }


# -------------------- CASHBOX --------------------
@pytest.fixture(scope="function")
def seed_cashbox():
    """
    Гарантирует, что в БД есть хотя бы одна касса
    """
    db = SessionLocal()

    cashbox = db.query(Cashbox).first()
    if not cashbox:
        cashbox = Cashbox(name="pytest-cashbox")
        db.add(cashbox)
        db.commit()
        db.refresh(cashbox)

    db.close()
    return cashbox
