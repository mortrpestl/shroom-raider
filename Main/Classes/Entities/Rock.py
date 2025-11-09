from Classes.Entity import Entity
from Classes.Grid import Grid
from Classes.Entities.import_entities import import_entities


class Rock(Entity):
    # * Attributes
    _is_collectable = False
    _is_collideable = True
    _is_pushable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "R"):
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
        if isinstance(pusher, entities["Player"]):
            return True
        else:
            return False

    # * Simple Setters

    # * Complex Setters
    def set_pos(self, direction: str):
        if super().set_pos(direction):
            entities = import_entities({"Water", "PavedTile"})
            on_grid = self.get_on_grid()
            r, c = self.get_pos()

            object_below = self.get_entity_below()
            if not object_below:
                return True

            if isinstance(object_below, entities["Water"]):  # Is the Rock on Water?
                new_paved_tile = entities["PavedTile"]((r, c), self.get_on_grid(), "-")
                self.destroy()  # Destroy Rock
                object_below.destroy()  # Destroy Water
                on_grid.add_layer_to_coord(r, c, new_paved_tile)  # Add new paved tile
            return True
        else:
            return False
