"""Pydantic v2 schemas for the ``Screen`` slice."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScreenCreate(BaseModel):
    theater_id: uuid.UUID
    name: str = Field(min_length=1, max_length=100)


class ScreenUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class ScreenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    theater_id: uuid.UUID
    name: str
    created_at: datetime
