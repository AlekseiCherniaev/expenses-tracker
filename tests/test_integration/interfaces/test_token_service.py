from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import jwt
import pytest

from expenses_tracker.domain.entities.user import User
from expenses_tracker.infrastructure.security.jwt_token_service import JWTTokenService


@pytest.fixture(params=["jwt_token_service"])
def token_service(request):
    with patch("expenses_tracker.core.settings.get_settings") as mock_settings:
        mock_settings.return_value = Mock(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
        )
    match request.param:
        case "jwt_token_service":
            return JWTTokenService()
        case _:
            raise ValueError(f"Unknown token_service {request.param}")


@pytest.fixture
def test_user():
    return User(
        id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


class TestTokenService:
    def test_create_and_decode_token_success(self, token_service, test_user):
        token = token_service.create_token(test_user)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded_payload = token_service.decode_token(token)

        assert decoded_payload.sub == test_user.username
        assert datetime.fromtimestamp(decoded_payload.exp, timezone.utc) > datetime.now(
            timezone.utc
        )

    def test_decode_invalid_token_raises_exception(self, token_service):
        invalid_token = "invalid.token.here"

        with pytest.raises(jwt.InvalidTokenError):
            token_service.decode_token(invalid_token)

    def test_decode_expired_token_raises_exception(self, token_service, test_user):
        with patch(
            "expenses_tracker.infrastructure.security.jwt_token_service.datetime"
        ) as mock_datetime:
            past_time = datetime.now(timezone.utc) - timedelta(hours=1)
            mock_datetime.now.return_value = past_time
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            with patch(
                "expenses_tracker.infrastructure.security.jwt_token_service.timedelta"
            ) as mock_timedelta:
                mock_timedelta.return_value = timedelta(minutes=-1)
                expired_token = token_service.create_token(test_user)

        with pytest.raises(jwt.ExpiredSignatureError):
            token_service.decode_token(expired_token)
