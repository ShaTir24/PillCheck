import uuid

from fastapi import Header, HTTPException, status
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

_BEARER_PREFIX = "Bearer "


def _decode_supabase_jwt(token: str) -> uuid.UUID:
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        # Supabase Auth's `sub` claim is the auth user id. PillCheck treats it as the
        # profile id directly (profile rows are keyed on the Supabase user id) rather
        # than maintaining a separate auth<->profile mapping table.
        return uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


async def get_current_profile_id(
    authorization: str | None = Header(default=None),
    x_debug_profile_id: str | None = Header(default=None),
) -> uuid.UUID:
    """Resolve the caller's profile id from a Supabase Auth bearer token.

    Local dev escape hatch: with no SUPABASE_JWT_SECRET configured, an
    X-Debug-Profile-Id header is accepted instead so the API is usable before
    Supabase Auth is wired up on the mobile client. Refuses the header once a
    secret is configured, so this never becomes an accidental prod bypass.
    """
    if not settings.supabase_jwt_secret:
        if settings.environment != "local":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_JWT_SECRET is not configured",
            )
        if not x_debug_profile_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-Debug-Profile-Id header required in local dev without auth configured",
            )
        return uuid.UUID(x_debug_profile_id)

    if not authorization or not authorization.startswith(_BEARER_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return _decode_supabase_jwt(authorization[len(_BEARER_PREFIX) :])
