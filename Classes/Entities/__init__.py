from .Axe import Axe
from .Flamethrower import Flamethrower
from .PavedTile import PavedTile
from .Player import Player
from .Stone import Stone
from .Tree import Tree
from .Water import Water
from .Mushroom import Mushroom

__all__ = [
    "Axe",
    "Flamethrower",
    "PavedTile",
    "Player",
    "Stone",
    "Tree",
    "Water", 
    "Mushroom"
]

# add newly-made files under Entities under "__all__" to make the 'from Classes.Entities import *' to work
