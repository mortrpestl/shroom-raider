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
        self.destroy()

    # * Complex Setter
    def burn_connected(self, visited: set | None = None):
        """Burns all orthogonally connected Trees

        Args:
            visited: The set of Trees that have already been burnt

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
