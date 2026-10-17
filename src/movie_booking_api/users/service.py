from __future__ import annotations

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from movie_booking_api.users.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from movie_booking_api.users.models import User
from movie_booking_api.users.schemas import UserCreate, UserLogin

password_hash = PasswordHash.recommended()


async def create_user(
    db: AsyncSession,
    data: UserCreate,
) -> User:
    """Create a new user with a securely hashed password."""

    result = await db.execute(select(User).where(User.email == data.email))

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise UserAlreadyExistsError(f"User with email {data.email} already exists")

    user = User(
        email=data.email,
        password_hash=password_hash.hash(data.password),
        full_name=data.full_name,
    )

    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    data: UserLogin,
) -> User:
    """Authenticate a user using email and password."""

    result = await db.execute(select(User).where(User.email == data.email))

    user = result.scalar_one_or_none()

    if user is None or not password_hash.verify(
        data.password,
        user.password_hash,
    ):
        raise InvalidCredentialsError("Invalid email or password")

    return user
