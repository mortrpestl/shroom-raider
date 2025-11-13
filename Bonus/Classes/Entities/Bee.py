from collections import deque
from Classes.Entity import Entity
import Utils.sounds as s


class Bee(Entity):
    _all_bees = []

    def __init__(self, pos, on_grid, lag, ascii=">"):
        super().__init__(pos, on_grid, ascii)
        self._is_deadly = True
        self._lag = int(lag)
        self._buffer = deque()  # cells for player
        self._is_explodable = True

        Bee._all_bees.append(self)

    def update(self):
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
            s.bee_death_sound()
            player.kill()

    @staticmethod
    def update_all():
        for bee in Bee._all_bees:
            bee.update()

    @staticmethod
    def remove_bee(bee):
        if bee in Bee._all_bees:
            Bee._all_bees.remove(bee)

    def destroy(self):
        super().destroy()
        Bee.remove_bee(self)
