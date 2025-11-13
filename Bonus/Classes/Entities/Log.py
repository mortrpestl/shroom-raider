from Classes.Entity import Entity
from Classes.Grid import Grid
from Classes.Entities.import_entities import import_entities
import Utils.sounds as s

class Log(Entity):
    # * Attributes
    _is_pushable = True
    _is_collideable = True
    _is_explodable = True
    _is_burnable = True

    def __init__(self, pos: list[int], on_grid: Grid, ascii="o"):
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_movement_validity(self, direction: str, r: int, c: int):
        if not self.in_bounds(r, c):
            return False

        target_obj = self.get_obj_in_coord(r, c)

        if target_obj is None:
            return True

        if target_obj.get_collectable():
            return False  # cannot move on collectables.

        return super().get_movement_validity(direction, r, c)

    def get_pushable(self, pusher: Entity):
        entities = import_entities({"Player"})
        if isinstance(pusher, (entities["Player"], Log)):
            s.log_sound()
            return True
        else:
            return False
        
    def chop(self):
        s.axe_sound()
        self.destroy()