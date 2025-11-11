from Classes.Entity import Entity
from Classes.Entities.Bee import Bee


class Beehive(Entity):
    counter = 0

    def __init__(self, pos, on_grid, ascii="&", bee_count: int = 3, bee_lag: int = 3):
        # if you want to make a bee chain, make bee_count and bee_lag the same

        super().__init__(pos, on_grid, ascii)
        self._is_tile_trigger = True
        self._bee_count = int(bee_count)
        self._bee_lag = int(bee_lag)

    def __repr__(self):
        return f"{super().__repr__()} (bee angered! RUN)"

    def trigger(self, player):
        """
        Called when the player steps on this tile.
        Immediately spawns bee_count bees. Bees handle following the player.
        """
        grid = self.get_on_grid()
        for i in range(self._bee_count):
            Bee(
                player.get_pos().copy(),
                grid,
                lag=self._bee_lag * (1 + Beehive.counter) + i,
            )

        Beehive.counter += 1

        self.destroy()
