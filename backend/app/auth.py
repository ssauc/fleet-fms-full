from datetime import datetime, timedelta, timezone
from passlib.hash import bcrypt
from jose import jwt
from .settings import settings

ALGO = "HS256"

def hash_password(p: str) -> str:
    return bcrypt.hash(p)

def verify_password(p: str, h: str) -> bool:
    return bcrypt.verify(p, h)

def create_token(sub: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.api_jwt_expires_min)
    return jwt.encode({"sub": sub, "role": role, "exp": exp}, settings.api_jwt_secret, algorithm=ALGO)
