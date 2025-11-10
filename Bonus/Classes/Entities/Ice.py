from Classes.Entity import Entity
from Classes.Grid import Grid
from Classes.Entities.import_entities import import_entities


class Ice(Entity):
    # * Attributes
    _is_pushable = True
    _is_collideable = True
    _is_explodable = True

    def __init__(self, pos: list[int], on_grid: Grid, ascii="o"):
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_pushable(self, pusher: Entity):
        entities = import_entities({"Player"})
        if isinstance(pusher, (entities["Player"])):
            return True
        else:
            return False

    def get_movement_validity(self, direction: str, r: int, c: int):
        if not self.in_bounds(r, c):
            return False

        # get the object
        target_obj = self.get_obj_in_coord(r, c)

        # Is there nothing? then you are free to move
        if target_obj is None:
            return True

        # Is the object collideable, otherwise? then you cannot move to that.
        elif target_obj.get_collideable():
            return False

        # Ice cannot move to collectables
        elif target_obj.get_collectable():
            return False

        return super().get_movement_validity(direction, r, c)

    # * Complex Setters

    def set_pos(self, direction):
        moved = False
        while super().set_pos(direction):
            moved = True
        else:
            return moved
