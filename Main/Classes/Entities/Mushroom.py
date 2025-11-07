from Classes.Entity import Entity
from Classes.Grid import Grid

class Mushroom(Entity):

    # * Attributes
    _is_collectable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str ='+'):
        super().__init__(pos, on_grid, ascii)

    # * Complex Setter
    def collect(self, p: Entity):
        p.increment_mushroom_count()
        self.destroy()