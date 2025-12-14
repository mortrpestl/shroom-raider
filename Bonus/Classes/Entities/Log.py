import Utils.sounds as s
from Classes.Entities.import_entities import import_entities
from Classes.Entity import Entity
from Classes.Grid import Grid


class Log(Entity):
    """An entity that can be pushed by the player and other logs.

    Attributes:
        See base class.

    """

    # * Attributes
    _is_pushable = True
    _is_collideable = True
    _is_explodable = True
    _is_burnable = True

    def __init__(self, pos: list[int], on_grid: Grid, ascii="o"):
        """Initializes Log object

        Args:
            See base class.

        """
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_movement_validity(self, direction: str, r: int, c: int):
        """Checks if a Log can be moved in a certain direction.

        Args:
            See parent class.

        Returns:
            True if the Log is able to move, False if not

        """
        if not self.in_bounds(r, c):
            return False

        target_obj = self.get_obj_in_coord(r, c)

        if target_obj is None:
            return True

        if target_obj.get_collectable():
            return False  # cannot move on collectables.

        return super().get_movement_validity(direction, r, c)

    def get_pushable(self, pusher: Entity):
        """Checks if pushable by the pusher

        Logs can only be moved by other Logs and the Player!

        Args:
            See parent class.

        """
        entities = import_entities({"Player"})
        if isinstance(pusher, (entities["Player"], Log)):
            s.log_sound()
            return True
        else:
            return False

    def chop(self):
        """Destroys a log when an axe is equipped."""
        s.axe_sound()
        self.destroy()
