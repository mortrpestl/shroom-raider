from Classes.Entity import Entity


class Tree(Entity):
    """Inherits Entity. Acts as an obstacle for other collideable Entities.
    
    Trees can be destroyed by a Player who is holding an Axe or Flamethrower.

    Attributes:
        See Base class.
    """

    def __init__(self, coord, on_grid, ascii='T'):
        """Initializes a Tree object.

        Args:
            See Base class.
        """
        super().__init__(coord, on_grid, ascii)

    def burn_connected(self, visited=None):
        """Burns all connected Tree instances

        Args:
            grid_obj_map: (See Grid) A list containing the Entities arranged by their position values.
        """
        if visited is None:
            visited = set()
        grid = self.get_on_grid()
        obj_map = grid.get_obj_map()

        r,c = self.get_pos()
        visited.add((r, c))
        self.destroy()

        for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(obj_map) and 0 <= nc < len(obj_map[0]):
                neighbor = obj_map[nr][nc]
                if isinstance(neighbor, Tree) and (nr, nc) not in visited:
                    neighbor.burn_connected(obj_map, visited)
        

                    
