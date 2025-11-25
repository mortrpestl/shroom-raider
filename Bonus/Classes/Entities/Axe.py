from Classes.Entity import Entity
from Classes.Grid import Grid


class Axe(Entity):
    """A storable Entity that, if used by the player, destroys a tree

    Attributes:
        See parent class

    """

    # * Attributes
    _is_collectable = True
    _is_storable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "x"):
        """Initializes Axe object
        
        Args:
            See parent class.

        """
        super().__init__(pos, on_grid, ascii)
