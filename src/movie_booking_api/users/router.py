from __future__ import annotations

from fastapi import APIRouter, status

from movie_booking_api.api.deps import CurrentUser, DbSession
from movie_booking_api.core.security import create_access_token
from movie_booking_api.users.models import User
from movie_booking_api.users.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from movie_booking_api.users.service import authenticate_user, create_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: UserCreate,
    db: DbSession,
) -> User:
    """Register a new user."""

    return await create_user(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login_user(
    data: UserLogin,
    db: DbSession,
) -> TokenResponse:
    """Authenticate a user and return an access token."""

    user = await authenticate_user(db, data)

    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
    )


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> User:
    """Return the currently authenticated user."""
    return current_user
