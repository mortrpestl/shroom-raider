import Utils.sounds as s
from Classes.Entity import Entity


class Flash(Entity):
    """When picked up, can be used to light up the map temporarily.

    Args:
        _active:
        _placed_pos: Determines the position where the flash will propagate.
        _current_radius: The current radius of the flashlight.

    """

    # * Attributes
    _is_collectable = True
    _is_storable = True
    _is_passive = True

    leeway = 5

    def __init__(self, pos, on_grid, ascii="?"):
        """Initializes a Flash object

        Args:
            See parent class.
        """
        super().__init__(pos, on_grid, ascii)
        self._active = False
        self._placed_pos = None
        self._current_radius = 0
        grid = self.get_on_grid()
        rows = len(grid.get_grid_obj_map())
        cols = len(grid.get_grid_obj_map()[0])
        self._max_radius = (cols + rows) // 2

    # * Complex Functions

    def use(self):
        """Activate flash at player position"""
        s.flash_sound()
        player_pos = self.get_on_grid().get_player_pos()
        self._placed_pos = list(player_pos)
        self._current_radius = self._max_radius
        self._active = True
        # register in grid for visualization only

        self.get_on_grid().register_flash(self)

    # * Simple Getters
    def get_radius(self):
        """Gets radius of flash, 0 if not active"""
        return self._current_radius if self._active else 0

    def get_pos(self):
        """Gets the placed position if active; otherwise, the world position"""
        return self._placed_pos if self._active else super().get_pos()

    # * Simple Setters
    def update_radius(self):
        """Decrement radius every render"""
        if not self._active:
            return
        if self._current_radius > 0:
            self._current_radius -= 1
        if self._current_radius == 0:
            self._active = False
            self._placed_pos = None
