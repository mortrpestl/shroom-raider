from classes.entity import Entity
from classes.grid import Grid


class Axe(Entity):
    """A storable Entity that, if used by the player, destroys a tree

    Attributes:
        See parent class

    """

    _is_collectable = True
    _is_storable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "x"):
        super().__init__(pos, on_grid, ascii)
