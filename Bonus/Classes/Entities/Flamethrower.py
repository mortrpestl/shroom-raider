from Classes.Entity import Entity
from Classes.Grid import Grid


class Flamethrower(Entity):
    """A storable Entity that, if used by the Player, destroys all connected burnable entities

    Attributes:
        See parent class.

    """

    # * Attributes
    _is_collectable = True
    _is_storable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "*"):
        """Initializes Flamethrower object.
        
        Args:
            See parent class.

        """
        super().__init__(pos, on_grid, ascii)
