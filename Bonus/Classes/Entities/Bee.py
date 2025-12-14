from collections import deque

import Utils.sounds as s
from Classes.Entity import Entity

# ! TODO: Documentation


class Bee(Entity):
    """Handles the Bee, an entity that follows the player's path given a bee lag and a bee count.
    Bees can be killed with Bombs and Flamethrowers.

    Args:
        _all_bees : Stores all Bee objects, "Master Bee list"
        _lag : Determines the game ticks before the bees spawn since stepping on beehive
        _buffer : Stores the coordinates of previous player positions

    """

    _all_bees = []

    def __init__(self, pos, on_grid, lag, ascii=">"):
        """Initializes a Bee object and appends it to all_bees

        Args:
            See base class.

        """
        super().__init__(pos, on_grid, ascii)
        self._is_deadly = True
        self._lag = int(lag)
        self._buffer = deque()  # cells for player
        self._is_explodable = True
        self._is_burnable = True

        Bee._all_bees.append(self)

    def update(self):
        """Update a bee's position."""
        grid = self.get_on_grid()
        player = grid.get_player()
        player_pos = player.get_pos()

        if not self._buffer or self._buffer[-1] != player_pos:
            self._buffer.append(player_pos)

        if len(self._buffer) <= self._lag:
            return

        s.bee_sound()
        target = self._buffer.popleft()

        curr_pos = self.get_pos()
        layers = grid.get_layers_from_coord(*curr_pos)
        if self in layers:
            layers.remove(self)

        grid.add_layer_to_coord(*target, self)
        self.set_coordinate(*target)

        target_layers = grid.get_layers_from_coord(*target)
        if player in target_layers:
            player.kill()

    @staticmethod
    def update_all():
        """Update all bee positions."""
        for bee in Bee._all_bees:
            bee.update()

    @staticmethod
    def remove_bee(bee):
        """Remove a bee from the master bee list"""
        if bee in Bee._all_bees:
            Bee._all_bees.remove(bee)

    def destroy(self):
        """See base class. Also removes the bee from master bee list"""
        super().destroy()
        Bee.remove_bee(self)
