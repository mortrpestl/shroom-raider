from Classes.Entity import Entity
from Classes.Grid import Grid

# * RUFF CHECKED: No errors (12/10/2025)


class Water(Entity):
    """A deadly entity that kills the player if stepped on.

    Attributes:
        See parent class.

    """

    # * Attributes
    _is_deadly = True

    def __init__(self, pos: list, on_grid: Grid, ascii_char: str = "~") -> None:
        """Initialize a Water object.

        Args:
            pos: [r, c] position on the grid.
            on_grid: The grid containing the water.
            ascii_char: The ascii character for the water.

        """
        super().__init__(pos, on_grid, ascii_char)
