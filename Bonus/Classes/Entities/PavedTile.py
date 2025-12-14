from Classes.Entity import Entity
from Classes.Grid import Grid


class PavedTile(Entity):
    """An Entity that is created when rock or ice goes over water. Can be walked on

    Attributes:
        See parent class.

    """

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "_"):
        super().__init__(pos, on_grid, ascii)
