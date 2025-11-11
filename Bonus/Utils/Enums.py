from enum import Enum

class ExitCodes(Enum):
    VICTORY = 0
    DEFEAT = 2
    QUIT = 3 
    INVALID = 4

class DisplayMode(Enum):
    EMOJI = 0
    ASCII = 1
    COLORED_ASCII = 2
