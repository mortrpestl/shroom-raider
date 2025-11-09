from Classes.Entity import Entity
from Classes.Grid import Grid
from Utils.general_utils import wait
import Utils.sounds as s



class Tree(Entity):
    # * Attributes
    _is_collideable = True
    _is_burnable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "T"):
        super().__init__(pos, on_grid, ascii)

    # * Simple Setter
    def chop(self):
        s.axe_sound()
        self.destroy()

    # * Complex Setter
    def burn_connected(self, visited: set | None = None):
        if visited is None:
            visited = set()

        grid = self.get_on_grid()
        obj_map = grid.get_grid_obj_map()

        r, c = self.get_pos()
        visited.add((r, c))
        self.destroy()
        grid.set_display_in_coord(*self.get_pos(), "🔥" if grid.get_display_mode() == "emoji" else "&")
        grid.render()
        wait(0.075)
        grid.add_active_flame(*self.get_pos())
        wait(0.075)
        

        for delta_row, delta_column in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_row, new_column = r + delta_row, c + delta_column

            if 0 <= new_row < len(obj_map) and 0 <= new_column < len(obj_map[0]):
                neighbor = obj_map[new_row][new_column][-1]
                if isinstance(neighbor, Tree) and (new_row, new_column) not in visited:
                    neighbor.burn_connected(visited)

                    
