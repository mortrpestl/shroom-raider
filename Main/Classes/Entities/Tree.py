from classes.entity import Entity
from classes.Grid import Grid

# * RUFF CHECKED: No errors (12/10/2025)


class Tree(Entity):
    """A collideable and burnable entity that can be destroyed by the player.

    Default character is 'T'

    Attributes:
        See parent class.

    """

    # * Attributes
    _is_collideable = True
    _is_burnable = True

    def __init__(self, pos: list, on_grid: Grid, ascii_char: str = "T") -> None:
        """Initialize a Tree object.

        Args:
            pos: [r, c] position on the grid.
            on_grid: The grid containing the tree.
            ascii_char: The ascii character for the tree.

        """
        super().__init__(pos, on_grid, ascii_char)

    # * Simple Setter
    def chop(self) -> None:
        """Destroy the tree and remove it from its grid."""
        self.destroy()

    # * Complex Setter
    def burn_connected(self, visited: set | None = None) -> None:
        """Burn all orthogonally connected trees.

        Args:
            visited: Set of coordinates already visited.

        """
        if visited is None:
            visited = set()

        grid = self.get_on_grid()
        obj_map = grid.get_grid_obj_map()

        r, c = self.get_pos()
        visited.add((r, c))
        self.destroy()

        for delta_row, delta_column in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_row, new_column = r + delta_row, c + delta_column

            if 0 <= new_row < len(obj_map) and 0 <= new_column < len(obj_map[0]):
                neighbor = obj_map[new_row][new_column][-1]
                if isinstance(neighbor, Tree) and (new_row, new_column) not in visited:
                    neighbor.burn_connected(visited)
