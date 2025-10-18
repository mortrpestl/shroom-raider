from Classes.Entity import Entity


class Tree(Entity):
    """Inherits Entity. Acts as an obstacle for other collideable Entities.
    
    Trees can be destroyed by a Player who is holding an Axe or Flamethrower.

    Attributes:
        See Base class.
        neighbors: A set containing the neighboring Trees of a Tree
    """

    def __init__(self, coord, on_grid):
        """Initializes a Tree object.

        Args:
            See Base class.
        """
        super().__init__(coord, on_grid)
        self.neighbors = set()

    def find_neighbors(self,__grid_obj_map):
        """Finds neighboring Tree instances of a Tree instance.

        Adds valid neighboring Tree instances to attribute neighbor
        
        Args:
            grid_obj_map: (See Grid) A list containing the Entities arranged by their position values.
        """
        drcs = [(1,1),(1,-1),(-1,1),(-1,-1)]

        def in_bounds(r,c): return 0<=r<len(__grid_obj_map) and 0<=c<len(__grid_obj_map[0])

        for dr,dc in drcs:
            r,c = self.get_pos()
            nr,nc = r+dr,c+dc
            if in_bounds(nr,nc):
                neighbor = __grid_obj_map[nr][nc]
                if isinstance(neighbor, Tree):
                    self.neighbors.add(neighbor)
                    
