"""Domain errors for the bookings slice."""

from __future__ import annotations

import uuid


class BookingError(Exception):
    """Base class for booking domain errors."""


class ShowNotFoundError(BookingError):
    def __init__(self, show_id: uuid.UUID) -> None:
        self.show_id = show_id
        super().__init__(f"Show {show_id} not found")


class SeatNotFoundError(BookingError):
    def __init__(self, seat_id: uuid.UUID) -> None:
        self.seat_id = seat_id
        super().__init__(f"Seat {seat_id} not found")


class SeatUnavailableError(BookingError):
    def __init__(self, seat_ids: list[uuid.UUID]) -> None:
        self.seat_ids = seat_ids
        super().__init__(f"Seats are already booked: {seat_ids}")


class BookingNotFoundError(BookingError):
    def __init__(self, booking_id: uuid.UUID) -> None:
        self.booking_id = booking_id
        super().__init__(f"Booking {booking_id} not found")


class BookingPermissionError(BookingError):
    """Raised when a user cannot access or modify a booking."""


class InvalidSeatSelectionError(BookingError):
    """Raised when the selected seats are invalid for the requested show."""
