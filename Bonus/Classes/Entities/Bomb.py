from Classes.Entity import Entity


class Bomb(Entity):
    _is_collectable = True
    _is_storable = True
    _is_passive = True

    def __init__(self, pos, on_grid, ascii="!"):
        super().__init__(pos, on_grid, ascii)
        self._active = False
        self._bomb_radius = 3
        self._placed_pos = None

    def __repr__(self):
        return f"{super().__repr__()} (with detonation radius: {self.get_radius()})"

    def get_radius(self):
        return self._bomb_radius

    def increment_radius(self):
        self._bomb_radius += 3

    def use(self):
        """
        Activates the bomb at the player's position and destroys nearby entities.
        """
        on_grid = self.get_on_grid()
        pr, pc = on_grid.get_player_pos()

        self._active = True
        self._placed_pos = (pr, pc)

        for r in range(pr - self.get_radius(), pr + self.get_radius() + 1):
            for c in range(pc - self.get_radius(), pc + self.get_radius() + 1):
                if not self.in_bounds(r, c):
                    continue

                if abs(r - pr) + abs(c - pc) > self.get_radius():
                    continue

                target = self.get_obj_in_coord(r, c)
                if target is None or target is self:
                    continue
                if target.__class__.__name__ == "Player":
                    continue
                if target.get_collideable() or target.get_collectable():
                    target.destroy()

        self._active = False
        self._placed_pos = None
        self.destroy()
