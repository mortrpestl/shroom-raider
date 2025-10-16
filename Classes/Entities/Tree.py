from Classes.Entity import Entity


class Tree(Entity):
    def __init__(self, coord, on_grid):
        super().__init__(coord, on_grid)
        self.neighbors = set()

    def find_neighbors(self,__grid_obj_map):
        drcs = [(1,1),(1,-1),(-1,1),(-1,-1)]

        def in_bounds(r,c): return 0<=r<len(__grid_obj_map) and 0<=c<len(__grid_obj_map[0])

        for dr,dc in drcs:
            r,c = self.get_pos()
            nr,nc = r+dr,c+dc
            if in_bounds(nr,nc):
                neighbor = __grid_obj_map[nr][nc]
                if isinstance(neighbor, Tree):
                    self.neighbors.add(neighbor)
                    
