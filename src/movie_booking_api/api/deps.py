"""Shared FastAPI dependencies."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.core.config import Settings, get_settings
from movie_booking_api.core.security import ALGORITHM
from movie_booking_api.db.session import get_db
from movie_booking_api.users.models import User, UserRole

DbSession = Annotated[AsyncSession, Depends(get_db)]

SettingsDep = Annotated[Settings, Depends(get_settings)]

bearer_scheme = HTTPBearer()

BearerToken = Annotated[
    HTTPAuthorizationCredentials,
    Depends(bearer_scheme),
]


async def get_current_user(
    db: DbSession,
    credentials: BearerToken,
    settings: SettingsDep,
) -> User:
    """Get the currently authenticated user from the JWT."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials.scheme.lower() != "bearer":
        raise credentials_exception

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "access":
            raise credentials_exception

        subject = payload.get("sub")

        if not isinstance(subject, str):
            raise credentials_exception

        user_id = uuid.UUID(subject)

    except InvalidTokenError, ValueError:
        raise credentials_exception from None

    result = await db.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


# Authentication dependency:
# Identifies the currently logged-in user.
CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


# Authorization dependency:
# Checks whether the current user has an allowed role.
def require_role(
    *allowed_roles: UserRole,
) -> Callable[..., Awaitable[User]]:
    """Require the current user to have one of the specified roles."""

    async def role_checker(
        current_user: CurrentUser,
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker


# Only ADMIN users can access endpoints using AdminUser.
AdminUser = Annotated[
    User,
    Depends(require_role(UserRole.ADMIN)),
]


# ADMIN and THEATER_OWNER can access endpoints using TheaterOwnerUser.
TheaterOwnerUser = Annotated[
    User,
    Depends(
        require_role(
            UserRole.ADMIN,
            UserRole.THEATER_OWNER,
        )
    ),
]
