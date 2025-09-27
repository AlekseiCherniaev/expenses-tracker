import structlog
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from expenses_tracker.application.interfaces.email_service import IEmailService
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.exceptions.auth import EmailSendingError

logger = structlog.get_logger(__name__)


class FastapiEmailService(IEmailService):
    def __init__(self) -> None:
        self.conf = ConnectionConfig(
            MAIL_USERNAME=str(get_settings().sender_email),
            MAIL_PASSWORD=get_settings().email_password,
            MAIL_FROM=get_settings().sender_email,
            MAIL_PORT=get_settings().smtp_port,
            MAIL_SERVER=get_settings().smtp_host,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        self.fastmail = FastMail(self.conf)
        logger.info("FastapiEmailService initialized")

    async def send_verification_email(self, to: EmailStr, token: str) -> None:
        verification_link = (
            f"https://{get_settings().domain}/api/auth/verify-email?email_token={token}"
        )

        message = MessageSchema(
            subject="Verify your email",
            recipients=[to],
            body=f"""
                <p>Hello!</p>
                <p>Please click the link below to verify your email:</p>
                <a href="{verification_link}">Verify Email</a>
            """,
            subtype=MessageType.html,
        )

        try:
            await self.fastmail.send_message(message)
            logger.bind(to=to).info("Verification email sent")
        except Exception as e:
            logger.bind(to=to, e=e).error("Failed to send email")
            raise EmailSendingError(f"Failed to send verification email to {to}") from e

    async def send_password_reset_email(self, to: EmailStr, token: str) -> None:
        reset_link = f"https://{get_settings().domain}/auth/reset-password?password_token={token}"

        message = MessageSchema(
            subject="Reset your password",
            recipients=[to],
            body=f"""
                <p>Hello!</p>
                <p>Please click the link below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
            """,
            subtype=MessageType.html,
        )

        try:
            await self.fastmail.send_message(message)
            logger.bind(to=to).info("Password reset email sent")
        except Exception as e:
            logger.bind(to=to, e=e).error("Failed to send email")
            raise EmailSendingError(
                f"Failed to send password reset email to {to}"
            ) from e
