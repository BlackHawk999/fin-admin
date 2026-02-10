import os
import pytest
from fastapi.testclient import TestClient

# ВАЖНО: env ставим ДО импорта app
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret")   # если у тебя есть такая настройка
os.environ.setdefault("ALGORITHM", "HS256")          # если используешь JWT
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.auth import get_password_hash


@pytest.fixture(scope="session", autouse=True)
def _create_test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    # можно не дропать, но если хочешь:
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create test client - pass app as positional argument, not keyword argument"""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user():
    """Create a test user in the database"""
    db = SessionLocal()

    user = db.query(User).filter(User.username == "test_admin").first()
    if not user:
        user = User(
            username="test_admin",
            hashed_password=get_password_hash("test123"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    db.close()
    return {"username": "test_admin", "password": "test123"}