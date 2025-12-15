from Classes.Entity import Entity
from Classes.Grid import Grid

# * RUFF CHECKED: No errors (12/10/2025)


class Mushroom(Entity):
    """An Entity that can be collected by the player. Collecting all mushrooms in a Grid clears it.

    Default character is '+'

    Attributes:
        See parent class

    """

    _is_collectable = True

    def __init__(self, pos: list, on_grid: Grid, ascii_char: str = "+") -> None:
        super().__init__(pos, on_grid, ascii_char)

    # * Complex Setter
