import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import bcrypt
from fastapi import Header, HTTPException, status
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

_BEARER_PREFIX = "Bearer "

TokenType = Literal["access", "refresh"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


@dataclass
class TokenPayload:
    user_id: uuid.UUID
    token_version: int


def _create_token(
    user_id: uuid.UUID, token_version: int, token_type: TokenType, expires_delta: timedelta
) -> str:
    now = datetime.now(UTC)
    claims = {
        "sub": str(user_id),
        "tv": token_version,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return str(jwt.encode(claims, settings.auth_jwt_secret, algorithm="HS256"))


def create_access_token(user_id: uuid.UUID, token_version: int) -> str:
    expires_delta = timedelta(minutes=settings.auth_access_token_expire_minutes)
    return _create_token(user_id, token_version, "access", expires_delta)


def create_refresh_token(user_id: uuid.UUID, token_version: int) -> str:
    return _create_token(
        user_id, token_version, "refresh", timedelta(days=settings.auth_refresh_token_expire_days)
    )


def decode_token(token: str, expected_type: TokenType) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.auth_jwt_secret, algorithms=["HS256"])
        if payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type"
            )
        return TokenPayload(user_id=uuid.UUID(payload["sub"]), token_version=payload["tv"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


def extract_bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith(_BEARER_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return authorization[len(_BEARER_PREFIX) :]
