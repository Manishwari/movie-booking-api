import uuid


class ScreenError(Exception):
    """Base exception for screen-related errors."""


class ScreenNotFoundError(ScreenError):
    def __init__(self, screen_id: uuid.UUID) -> None:
        self.screen_id = screen_id
        super().__init__(f"Screen {screen_id} not found")
