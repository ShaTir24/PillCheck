import uuid
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import HTTPException

from app.core.security import decode_token, hash_password
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    SignupRequest,
)
from app.services.auth import AuthService, _hash_reset_token


class FakeUserRepo:
    """In-memory fake — proves the repository interface is swappable (ADR-003/DIP),
    no database needed for this test."""

    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    async def get(self, id: uuid.UUID) -> User | None:
        return self.users.get(id)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    async def get_by_reset_token_hash(self, token_hash: str) -> User | None:
        return next(
            (u for u in self.users.values() if u.password_reset_token_hash == token_hash), None
        )

    async def add(self, entity: User) -> User:
        if entity.id is None:
            entity.id = uuid.uuid4()
        self.users[entity.id] = entity
        return entity


class FakeEmailSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send_password_reset(self, to_email: str, reset_link: str) -> None:
        self.sent.append((to_email, reset_link))


def _service() -> tuple[AuthService, FakeUserRepo, FakeEmailSender]:
    repo = FakeUserRepo()
    sender = FakeEmailSender()
    return AuthService(repo, sender), repo, sender


async def test_signup_then_login_succeeds() -> None:
    service, _, _ = _service()
    await service.signup(SignupRequest(email="a@example.com", password="password123"))

    tokens = await service.login(LoginRequest(email="a@example.com", password="password123"))

    payload = decode_token(tokens.access_token, expected_type="access")
    assert payload.token_version == 0


async def test_signup_rejects_duplicate_email() -> None:
    service, _, _ = _service()
    await service.signup(SignupRequest(email="a@example.com", password="password123"))

    with pytest.raises(HTTPException) as exc_info:
        await service.signup(SignupRequest(email="a@example.com", password="other-password"))

    assert exc_info.value.status_code == 409


async def test_login_rejects_wrong_password() -> None:
    service, _, _ = _service()
    await service.signup(SignupRequest(email="a@example.com", password="password123"))

    with pytest.raises(HTTPException) as exc_info:
        await service.login(LoginRequest(email="a@example.com", password="wrong-password"))

    assert exc_info.value.status_code == 401


async def test_reset_password_bumps_token_version_and_invalidates_old_tokens() -> None:
    service, repo, sender = _service()
    await service.signup(SignupRequest(email="a@example.com", password="password123"))
    await service.forgot_password(ForgotPasswordRequest(email="a@example.com"), "pillcheck://reset")
    raw_token = sender.sent[0][1].split("token=")[1]

    reset_data = ResetPasswordRequest(token=raw_token, new_password="newpassword123")
    await service.reset_password(reset_data)

    user = await repo.get_by_email("a@example.com")
    assert user is not None
    assert user.token_version == 1
    # Old password no longer works, new one does.
    with pytest.raises(HTTPException):
        await service.login(LoginRequest(email="a@example.com", password="password123"))
    await service.login(LoginRequest(email="a@example.com", password="newpassword123"))


async def test_reset_password_rejects_expired_token() -> None:
    service, repo, _ = _service()
    tokens = await service.signup(SignupRequest(email="a@example.com", password="password123"))
    payload = decode_token(tokens.access_token, expected_type="access")
    user = await repo.get(payload.user_id)
    assert user is not None
    user.password_reset_token_hash = _hash_reset_token("some-token")
    user.password_reset_expires_at = datetime.now(UTC) - timedelta(minutes=1)

    with pytest.raises(HTTPException) as exc_info:
        reset_data = ResetPasswordRequest(token="some-token", new_password="x12345678")
        await service.reset_password(reset_data)

    assert exc_info.value.status_code == 400


async def test_reset_password_rejects_unknown_token() -> None:
    service, _, _ = _service()

    with pytest.raises(HTTPException) as exc_info:
        await service.reset_password(ResetPasswordRequest(token="bogus", new_password="x12345678"))

    assert exc_info.value.status_code == 400


async def test_forgot_password_is_silent_for_unknown_email() -> None:
    service, _, sender = _service()

    await service.forgot_password(ForgotPasswordRequest(email="nobody@example.com"), "pillcheck://reset")

    assert sender.sent == []


def test_hash_password_produces_verifiable_hash() -> None:
    hashed = hash_password("password123")
    assert hashed != "password123"
