import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.auth import get_password_hash


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


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
