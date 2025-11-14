from Classes.Entity import Entity
from Classes.Grid import Grid


class Mushroom(Entity):
    """
    An Entity that can be collected by the player. Collecting all mushrooms in a Grid clears it

    Attributes: 
        See parent class
    """
    _is_collectable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "+"):
        super().__init__(pos, on_grid, ascii)

    # * Complex Setter
