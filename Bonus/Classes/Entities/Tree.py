from Classes.Entity import Entity
from Classes.Grid import Grid
from Utils.general_utils import wait
import Utils.sounds as s


class Tree(Entity):
    # * Attributes
    _is_collideable = True
    _is_burnable = True
    _is_explodable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "T"):
        super().__init__(pos, on_grid, ascii)

    # * Simple Setter
    def chop(self):
        s.axe_sound()
        self.destroy()
