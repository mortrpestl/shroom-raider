from classes.entities.player import Player
from classes.entity import Entity
from classes.grid import Grid


class DummyPlayer(Player):
    """A Player subclass that never collects mushrooms and never dies.

    Useful for testing non-winning/non-losing scenarios.
    """

    def __init__(
        self,
        pos: list[int] | None = None,
        on_grid: Grid | None = None,
        ascii_char: str = "L",
        item: Entity | None = None,
    ) -> None:
        if pos is None:
            pos = [0, 0]
        super().__init__(pos, on_grid, ascii_char, item)

    def get_mushroom_count(self) -> int:
        return 0

    def get_is_dead(self) -> bool:
        return False


class WinPlayer(Player):
    """A Player subclass that immediately wins (collects all mushrooms)."""

    def __init__(
        self,
        on_grid: Grid,
        pos: list[int] | None = None,
        ascii_char: str = "L",
        item: Entity | None = None,
    ) -> None:
        if pos is None:
            pos = [0, 0]
        super().__init__(pos, on_grid, ascii_char, item)
        self.grid = on_grid

    def get_mushroom_count(self) -> int:
        return self.grid.get_total_mushrooms()

    def get_is_dead(self) -> bool:
        return False


class LosePlayer(Player):
    """A Player subclass that is always dead."""

    def __init__(
        self,
        pos: list[int] | None = None,
        on_grid: Grid | None = None,
        ascii_char: str = "L",
        item: Entity | None = None,
    ) -> None:
        if pos is None:
            pos = [0, 0]
        super().__init__(pos, on_grid, ascii_char, item)

    def get_mushroom_count(self) -> int:
        return 0

    def get_is_dead(self) -> bool:
        return True
