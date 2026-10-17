"""Pydantic v2 schemas for the ``Seat`` slice."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SeatCreate(BaseModel):
    screen_id: uuid.UUID
    seat_number: str = Field(min_length=1, max_length=10)


class SeatUpdate(BaseModel):
    seat_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=10,
    )


class SeatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    screen_id: uuid.UUID
    seat_number: str
    created_at: datetime
