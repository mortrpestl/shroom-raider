import Utils.sounds as s
from Classes.Entity import Entity
from Classes.Grid import Grid
from Utils.general_utils import wait


class Bomb(Entity):
    """Handles entities that destroy collidable surroundings when exploding.
    Also handles all bomb stacking functionality.

    Args:
        _active : A boolean that lets the bomb placed activate (then deactivate forever after being dropped).
        _bomb_radius : An int that stores how far the bomb affects its surroundings.
        _placed_pos : A pair of ints that takes note of where a bomb is dropped / triggered by the player.

    """

    _is_collectable = True
    _is_storable = True
    _is_passive = True

    def __init__(self, pos: list[int], on_grid: Grid, ascii: str = "!"):
        super().__init__(pos, on_grid, ascii)
        self._active = False
        self._bomb_radius = 3
        self._placed_pos = None

    def __repr__(self):
        return f"{super().__repr__()} (with detonation radius: {self.get_radius()})"

    def get_radius(self):
        """Returns bomb radius."""
        return self._bomb_radius

    def increment_radius(self):
        """Increments radius by 3 (default)."""
        self._bomb_radius += 3

    def use(self):
        """Activates the bomb at the player's position and destroys nearby entities.
        """
        on_grid = self.get_on_grid()
        pr, pc = on_grid.get_player_pos()

        self._active = True
        self._placed_pos = (pr, pc)

        for curr_radius in range(1, self.get_radius()):
            for r in range(pr - curr_radius, pr + curr_radius + 1):
                for c in range(pc - curr_radius, pc + curr_radius + 1):
                    if not self.in_bounds(r, c):
                        continue
                    if abs(r - pr) + abs(c - pc) != curr_radius:
                        continue
                    on_grid.add_active_blast(r, c)
                    target = self.get_obj_in_coord(r, c)
                    if target is None or target is self:
                        continue
                    if target.__class__.__name__ == "Player":
                        continue
                    if target.get_explodable():
                        target.destroy()
            on_grid.render()
            on_grid.smother_active_blasts()
            wait(0.125)
            s.bomb_sound()

        on_grid.clear_all_blasts()

        self._active = False
        self._placed_pos = None
        self.destroy()
