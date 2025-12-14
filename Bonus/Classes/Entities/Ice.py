import Utils.sounds as s
from Classes.Entities.import_entities import import_entities
from Classes.Entity import Entity
from Classes.Grid import Grid
from Utils.general_utils import wait


class Ice(Entity):
    """An entity that when pushed, continues until hitting an immovable entity.
    Like a rock, turns the tile below it to ice when the ice stops and it happens to be above water when this happens.

    Attributes:
        See parent class.

    """

    # * Attributes
    _is_pushable = True
    _is_collideable = True
    _is_explodable = True

    def __init__(self, pos: list[int], on_grid: Grid, ascii="0"):
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_pushable(self, pusher: Entity):
        """Overrides parent method. Adds the logic for sliding for the pushable logic.

        Args:
            See parent class.

        """
        entities = import_entities({"Player"})
        if isinstance(pusher, (entities["Player"], Ice)):
            return True
        else:
            return False

    def get_movement_validity(self, direction: str, r: int, c: int):
        """Checks if a Rock can be pushed in a certain direction

        Args:
            See parent class.

        """
        if not self.in_bounds(r, c):
            return False

        # get the object
        target_obj = self.get_obj_in_coord(r, c)

        # Is there nothing? then you are free to move
        if target_obj is None:
            return True

        # Is the object collideable, otherwise? then you cannot move to that.
        elif target_obj.get_collideable() or target_obj.get_collectable():
            return False

        return super().get_movement_validity(direction, r, c)

    # * Complex Setters

    def set_pos(self, direction):
        """Adds 'water turns to paved tile' mechanic to ice

        Continuously set position until stopped. If there is water below it, it paved the water.

        Args:
            direction: A string containing the direction the ice continues to move in

        Returns:
            moved: Whether the entity has moved or not

        """
        entities = import_entities({"Water", "PavedTile"})
        moved = False
        while super().set_pos(direction):
            moved = True
            self.get_on_grid().render()
            s.ice_sound()
            wait(0.075)
        object_below = self.get_entity_below()
        if object_below is None:
            return moved

        if isinstance(object_below, entities["Water"]):  # Is the Ice on Water?
            new_paved_tile = entities["PavedTile"](self.get_pos(), self.get_on_grid(), "-")
            self.destroy()  # Destroy Ice
            object_below.destroy()  # Destroy Water
            self.get_on_grid().add_layer_to_coord(*self.get_pos(), new_paved_tile)  # Add new paved tile

        return moved
