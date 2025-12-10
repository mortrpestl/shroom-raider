from classes.entities.import_entities import import_entities
from classes.entity import Entity
from classes.grid import Grid


class Rock(Entity):
    """A collideable Entity that can be pushed by the player if there are no other collideable or collectible Entities blocking it.

    Attributes:
        See parent class

    """

    # * Attributes
    _is_collectable = False
    _is_collideable = True
    _is_pushable = True

    def __init__(self, pos: list, on_grid: Grid, ascii: str = "R"):
        """Initializes a Rock object

        Args:
            See parent class

        """
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_movement_validity(self, direction: str, r: int, c: int):
        """Checks if a Rock can be pushed in a certain direction

        Args:
            direction: 'wasd', the intended direction of movement
            r, c: The row and column position of the Rock

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
