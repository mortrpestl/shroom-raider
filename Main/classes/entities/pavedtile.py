from classes.entity import Entity
from classes.grid import Grid

# * RUFF CHECKED: No errors (12/10/2025)


class PavedTile(Entity):
    """An Entity that is created when a rock goes over water. Can be walked on.

    Default character is '_'
    
    Attributes:
        See parent class.

    """

    def __init__(self, pos: list, on_grid: Grid, ascii_type: str = "_") -> None:
        super().__init__(pos, on_grid, ascii_type)
