import os
from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.hash import bcrypt

from app.db import get_db_connection  # kept for possible extensions

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
JWT_EXP_MIN = 60  # token validity in minutes

security = HTTPBearer()


def create_token(user_id: int, username: str, is_admin: bool) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXP_MIN)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = creds.credentials
    return decode_token(token)


def get_current_admin(payload: dict = Depends(get_current_user)) -> dict:
    if not payload.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return bcrypt.hash(plain)
