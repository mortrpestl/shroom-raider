import Utils.sounds as s
from Classes.Entities.import_entities import import_entities
from Classes.Entity import Entity
from Classes.Grid import Grid


class Rock(Entity):
    """A collideable Entity that can be pushed by the player 
    
    Rocks cannot be pushed if there are other collideable or collectable Entities blocking it.

    Attributes:
        See parent class
    """
    # * Attributes
    _is_collectable = False
    _is_collideable = True
    _is_pushable = True
    _is_explodable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "R"):
        """Initializes a Rock object

        Args:
            See parent class
        """
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_movement_validity(self, direction: str, r: int, c: int):
        """Checks if a Rock can be moved in a certain direction

        Args:
            See parent class.

        Returns:
            True if the rocks is able to move, False if not 
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
        """Checks if the rock is pushable by its pusher

        Args:
            pusher: The Entity trying to push the Rock

        Returns:
            A boolean indicating if the Rock is able to be pushed by its pusher
        """
        entities = import_entities({"Player"})
        if isinstance(pusher, entities["Player"]):
            return True
        else:
            return False

    # * Simple Setters

    # * Complex Setters
    def set_pos(self, direction: str):
        """Moves the Rock on the Grid

        Args: 
            direction: The direction that the Entity wants to move

        Returns:
            A boolean indicating whether the Rock was able to move or not
        """
        if super().set_pos(direction):
            s.push_sound()
            entities = import_entities({"Water", "PavedTile"})
            on_grid = self.get_on_grid()
            r, c = self.get_pos()

            object_below = self.get_entity_below()
            if not object_below:
                return True

            if isinstance(object_below, entities["Water"]):  # Is the Rock on Water?
                new_paved_tile = entities["PavedTile"]((r, c), self.get_on_grid(), "-")
                s.water_sound()
                self.destroy()  # Destroy Rock
                object_below.destroy()  # Destroy Water
                on_grid.add_layer_to_coord(r, c, new_paved_tile)  # Add new paved tile
            return True
        else:
            s.failpush_sound()
            return False
