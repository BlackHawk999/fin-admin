from app.database import SessionLocal
from app.models.user import User
from app.auth import get_password_hash

USERNAME = "Abbos"
PASSWORD = "abbosfin"

db = SessionLocal()

user = db.query(User).filter(User.username == USERNAME).first()
if not user:
    user = User(username=USERNAME, hashed_password=get_password_hash(PASSWORD))
    db.add(user)
    db.commit()
    print("✅ admin created")
else:
    user.hashed_password = get_password_hash(PASSWORD)
    db.commit()
    print("♻️ admin password reset")

db.close()
