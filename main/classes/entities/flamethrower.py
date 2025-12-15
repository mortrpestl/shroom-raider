from classes.entity import Entity
from classes.grid import Grid

# * RUFF CHECKED: No errors (12/10/2025)


class Flamethrower(Entity):
    """A storable Entity that, if used by the Player, destroys all connected trees.

    Default character is '*'

    Attributes:
        See parent class

    """

    # * Attributes
    _is_collectable = True
    _is_storable = True

    def __init__(self, pos: list, on_grid: Grid, ascii_char: str = "*") -> None:
        super().__init__(pos, on_grid, ascii_char)
