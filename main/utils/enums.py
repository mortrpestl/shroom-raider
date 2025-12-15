from enum import Enum


class ExitCodes(Enum):
    """Codes for finishing the game."""

    DEFEAT = 0
    VICTORY = 1
    INVALID = 2
