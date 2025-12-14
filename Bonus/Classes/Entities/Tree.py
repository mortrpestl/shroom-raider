import Utils.sounds as s
from Classes.Entity import Entity
from Classes.Grid import Grid


class Tree(Entity):
    """A collideable and burnable Entity that can be destroyed by the player using either the Axe or Flamethrower

    Attributes:
        See parent class

    """

    # * Attributes
    _is_collideable = True
    _is_burnable = True
    _is_explodable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "T"):
        """Initializes a Tree object

        Args:
            See parent class

        """
        super().__init__(pos, on_grid, ascii)

    # * Simple Setter
    def chop(self):
        """Destroys a Tree object, and removes it from its Grid
        """
        s.axe_sound()
        self.destroy()
