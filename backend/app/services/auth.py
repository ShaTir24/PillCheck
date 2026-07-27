import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from app.core.email import EmailSender
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)

_RESET_TOKEN_TTL = timedelta(minutes=30)


def _hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, repo: UserRepository, email_sender: EmailSender) -> None:
        self.repo = repo
        self.email_sender = email_sender

    def _issue_tokens(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user.id, user.token_version),
            refresh_token=create_refresh_token(user.id, user.token_version),
        )

    async def signup(self, data: SignupRequest) -> TokenResponse:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        password_hash = hash_password(data.password)
        new_user = User(email=data.email, password_hash=password_hash, token_version=0)
        user = await self.repo.add(new_user)
        return self._issue_tokens(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
        return self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user = await self.repo.get(payload.user_id)
        if user is None or user.token_version != payload.token_version:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
        return self._issue_tokens(user)

    async def forgot_password(self, data: ForgotPasswordRequest, reset_link_base: str) -> None:
        user = await self.repo.get_by_email(data.email)
        if user is None:
            return  # don't reveal whether the email is registered
        raw_token = secrets.token_urlsafe(32)
        user.password_reset_token_hash = _hash_reset_token(raw_token)
        user.password_reset_expires_at = datetime.now(UTC) + _RESET_TOKEN_TTL
        await self.repo.add(user)
        reset_link = f"{reset_link_base}?token={raw_token}"
        await self.email_sender.send_password_reset(user.email, reset_link)

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        user = await self.repo.get_by_reset_token_hash(_hash_reset_token(data.token))
        if (
            user is None
            or user.password_reset_expires_at is None
            or user.password_reset_expires_at < datetime.now(UTC)
        ):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")
        user.password_hash = hash_password(data.new_password)
        user.password_reset_token_hash = None
        user.password_reset_expires_at = None
        user.token_version += 1
        await self.repo.add(user)
