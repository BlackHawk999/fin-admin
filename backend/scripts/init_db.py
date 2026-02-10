"""
Create default admin user and seed cashboxes. Run: python -m scripts.init_db
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.cashbox import Cashbox
from app.auth import get_password_hash

CASHBOX_NAMES = [
    "cashbox_1_day",
    "cashbox_2_day",
    "cashbox_1_night",
    "cashbox_2_night",
]


def main():
    db = SessionLocal()
    try:
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "admin")
        if db.query(User).filter(User.username == username).first():
            print(f"User {username} already exists")
        else:
            user = User(
                username=username,
                hashed_password=get_password_hash(password),
            )
            db.add(user)
            print(f"Created user: {username}")

        for name in CASHBOX_NAMES:
            if db.query(Cashbox).filter(Cashbox.name == name).first():
                continue
            db.add(Cashbox(name=name))
            print(f"Created cashbox: {name}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
