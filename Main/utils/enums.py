from enum import Enum


class ExitCodes(Enum):
    """Codes for finishing the game."""

    VICTORY = 0
    DEFEAT = 2
    INVALID = 3
