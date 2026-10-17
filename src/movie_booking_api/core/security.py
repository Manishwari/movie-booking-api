from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from movie_booking_api.core.config import get_settings

settings = get_settings()

password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for a user."""

    expires_at = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "exp": expires_at,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )
