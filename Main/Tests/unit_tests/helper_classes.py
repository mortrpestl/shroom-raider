from classes.entities.player import Player
from classes.grid import Grid


class DummyPlayer(Player):
    """A Player subclass that never collects mushrooms and never dies.
    
    Useful for testing non-winning/non-losing scenarios.
    """

    def __init__(self, pos=[0, 0], on_grid: Grid = None, ascii="L", item=None):
        super().__init__(pos, on_grid, ascii, item)

    def get_mushroom_count(self):
        return 0

    def get_is_dead(self):
        return False


class WinPlayer(Player):
    """A Player subclass that immediately wins (collects all mushrooms)."""

    def __init__(self, on_grid: Grid, pos=[0, 0], ascii="L", item=None):
        super().__init__(pos, on_grid, ascii, item)
        self.grid = on_grid

    def get_mushroom_count(self):
        return self.grid.get_total_mushrooms()

    def get_is_dead(self):
        return False


class LosePlayer(Player):
    """A Player subclass that is always dead."""

    def __init__(self, pos=[0, 0], on_grid: Grid = None, ascii="L", item=None):
        super().__init__(pos, on_grid, ascii, item)

    def get_mushroom_count(self):
        return 0

    def get_is_dead(self):
        return True
