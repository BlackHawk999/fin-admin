from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models.user import User

settings = get_settings()

# bcrypt_sha256 НЕ имеет лимита 72 байта как обычный bcrypt
# bcrypt оставляем для обратной совместимости (если в базе есть старые хэши)
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

security = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    # защита на случай если сюда прилетела не строка
    password = "" if password is None else str(password)
    print("HASHING LEN:", len(password), "VALUE_PREVIEW:", str(password)[:30])
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # защита от перепутанных аргументов
    p = "" if plain_password is None else str(plain_password)
    h = "" if hashed_password is None else str(hashed_password)

    looks_like_hash_p = p.startswith("$2") or p.startswith("$bcrypt-sha256$")
    looks_like_hash_h = h.startswith("$2") or h.startswith("$bcrypt-sha256$")

    if looks_like_hash_p and not looks_like_hash_h:
        p, h = h, p

    try:
        return pwd_context.verify(p, h)
    except ValueError:
        # например: password cannot be longer than 72 bytes (старый bcrypt)
        return False


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
