from Classes.Entity import Entity


class Tree(Entity):

    # * Attributes
    _is_collideable = True
    _is_burnable = True

    def __init__(self, coord, on_grid, ascii='T'):

        super().__init__(coord, on_grid, ascii)

    # * Simple Setter
    def chop(self): self.destroy()

    # * Complex Setter
    def burn_connected(self, visited=None):

        if visited is None:
            visited = set()
            
        grid = self.get_on_grid()
        obj_map = grid.get_grid_obj_map()

        r,c = self.get_pos()
        visited.add((r, c))
        self.destroy()

        for delta_row,delta_column in [(1,0), (-1,0), (0,1), (0,-1)]:
            new_row , new_column = r+delta_row, c+delta_column

            if 0<= new_row <len(obj_map) and 0 <= new_column < len(obj_map[0]):
                neighbor = obj_map[new_row][new_column][-1]
                if isinstance(neighbor,Tree) and (new_row,new_column) not in visited:
                    neighbor.burn_connected(visited)

    
        

                    
