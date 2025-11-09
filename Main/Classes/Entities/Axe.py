from Classes.Entity import Entity
from Classes.Grid import Grid


class Axe(Entity):
    # * Attributes
    _is_collectable = True
    _is_storable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "x"):
        super().__init__(pos, on_grid, ascii)
