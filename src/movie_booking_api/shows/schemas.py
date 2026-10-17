"""Pydantic v2 schemas for the ``Show`` slice."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ShowCreate(BaseModel):
    movie_id: uuid.UUID
    screen_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    ticket_price: float = Field(gt=0)


class ShowUpdate(BaseModel):
    movie_id: uuid.UUID | None = None
    screen_id: uuid.UUID | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    ticket_price: float | None = Field(default=None, gt=0)


class ShowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    movie_id: uuid.UUID
    screen_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    ticket_price: float
