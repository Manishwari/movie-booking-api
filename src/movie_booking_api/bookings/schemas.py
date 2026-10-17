"""Request and response schemas for bookings."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from movie_booking_api.bookings.models import BookingStatus


class BookingCreate(BaseModel):
    """Request body for creating a booking."""

    show_id: uuid.UUID
    seat_ids: list[uuid.UUID] = Field(min_length=1)


class BookingRead(BaseModel):
    """Booking details returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    show_id: uuid.UUID
    status: BookingStatus
    total_amount: Decimal
    created_at: datetime
    seat_ids: list[uuid.UUID] = Field(default_factory=list)


class BookingCancelResponse(BaseModel):
    """Response returned after cancelling a booking."""

    id: uuid.UUID
    status: BookingStatus
