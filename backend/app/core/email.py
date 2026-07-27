import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmailSender(ABC):
    """Outbound transactional email. Services depend on this, never on a provider
    SDK directly — swapping in SES later is a new class + one DI line in
    app/api/deps.py, no changes to app/services/auth.py (ADR-006)."""

    @abstractmethod
    async def send_password_reset(self, to_email: str, reset_link: str) -> None: ...


class LoggingEmailSender(EmailSender):
    """No email provider is configured yet — logs the reset link instead of
    sending it. Replace with an SESEmailSender once SES is set up.

    Uses warning level (not info) so it's visible under Python's default
    logging config — nothing in this app calls logging.basicConfig, so an
    info-level log here would be silently dropped.
    """

    async def send_password_reset(self, to_email: str, reset_link: str) -> None:
        logger.warning("Password reset requested for %s: %s", to_email, reset_link)
