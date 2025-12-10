from classes.entity import Entity
from classes.grid import Grid


class Water(Entity):
    """A deadly Entity that kills the player if stepped on

    Attributes:
        See parent class

    """

    # * Attributes
    _is_deadly = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "~"):
        """Initializes a Water object"""
        super().__init__(pos, on_grid, ascii)
