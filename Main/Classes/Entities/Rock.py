from classes.entities.import_entities import import_entities
from classes.entity import Entity
from classes.Grid import Grid

# * RUFF CHECKED: No errors (12/10/2025)


class Rock(Entity):
    """A collideable entity that can be pushed by the player.

    Default character is 'R'

    Attributes:
        See parent class

    """

    # * Attributes
    _is_collectable = False
    _is_collideable = True
    _is_pushable = True

    def __init__(self, pos: list, on_grid: Grid, ascii_char: str = "R") -> None:
        """Initialize a Rock object.

        Args:
            pos: [r, c] position on the grid.
            on_grid: The grid containing the rock.
            ascii_char: The ascii character for the rock.

        """
        super().__init__(pos, on_grid, ascii_char)

    # * Complex Getters

    def get_movement_validity(self, direction: str, r: int, c: int) -> bool:
        """Check if a Rock can be pushed in a certain direction.

        Args:
            direction: 'wasd', the intended direction of movement.
            r: The target row.
            c: The target column.

        Returns:
            True if the rock can move, False otherwise.

        """
        if not self.in_bounds(r, c):
            return False

        target_obj = self.get_obj_in_coord(r, c)

        if target_obj is None:
            return True

        if target_obj.get_collectable():
            return False  # cannot move on collectables.

        return super().get_movement_validity(direction, r, c)

    def get_pushable(self, pusher: Entity) -> bool:
        """Return whether the rock is pushable by the given pusher.

        Args:
            pusher: The Entity trying to push the Rock.

        Returns:
            True if the pusher may push the rock, otherwise False.

        """
        entities = import_entities({"Player"})
        return isinstance(pusher, entities["Player"])

    # * Simple Setters

    # * Complex Setters
    def set_pos(self, direction: str) -> bool:
        """Move the Rock on the Grid.

        Args:
            direction: The direction that the Entity wants to move.

        Returns:
            True if the rock moved, otherwise False.

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
