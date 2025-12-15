from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from classes.grid import Grid  # imported only for type checking to avoid circular imports


class Entity:
    """The superclass for all entities that exist in the game.

    Some functions in this class are overwritten by some of the child classes.

    Attributes:
        _is_collideable: If True, any other collideable object cannot occupy this Entity's space.
        _is_collectable: If True, Player can collect this Entity.
        _is_storable: If True, then Player can keep this in inventory.
        _is_pushable: If True, Player can push this Entity.
        _is_deadly: If True, Player gets game over'd when on it.
        _is_burnable: If True, triggers burning of Tree.

        __pos: [r, c], the row and column of the Grid where the entity is located.
        __on_grid: The Grid object that contains the entity.
        __ascii: The ascii symbol that represents the entity.

    """

    _is_collideable = False
    _is_collectable = False
    _is_storable = False
    _is_pushable = False
    _is_deadly = False
    _is_burnable = False

    def __init__(self, pos: list[int], on_grid: Grid, ascii_char: str) -> None:
        """Initialize an Entity object.

        Args:
            pos: [r, c], the row and column of the entity on the given Grid.
            on_grid: The grid which contains this entity.
            ascii_char: The ascii character which corresponds to this entity.

        """
        self.__pos: list[int] = list(pos)
        self.__on_grid: Grid = on_grid
        self.__ascii: str = ascii_char

    # * Simple Getters

    def get_ascii(self) -> str:
        """Return the ASCII character representation of the Entity.

        Returns:
            The ASCII character.

        """
        return self.__ascii

    def get_on_grid(self) -> Grid:
        """Return the Grid object that this Entity resides in.

        Returns:
            The Grid containing this entity.

        """
        return self.__on_grid

    def get_pos(self) -> list[int]:
        """Return the position [r, c] of this Entity in its Grid.

        Returns:
            The row/column pair for this entity.

        """
        return self.__pos

    def get_obj_in_coord(self, r: int, c: int) -> Entity | None:
        """Return the object on coordinate [r, c] on the same Grid as this Entity.

        Args:
            r (int): Row index.
            c (int): Column index.

        Returns:
            The entity at the given coordinate, or None if empty.

        """
        return self.__on_grid.get_obj_in_coord(r, c)

    """
    The following functions contain the simple getters for all the basic class attributes
    """

    def get_burnable(self) -> bool:
        """Return whether the object is burnable.

        Returns:
            True if burnable, otherwise False.

        """
        return bool(self._is_burnable)

    def get_collideable(self) -> bool:
        """Return whether the object is collideable.

        Returns:
            True if collideable (or pushable), otherwise False.

        """
        return bool(self._is_collideable or self._is_pushable)

    def get_collectable(self) -> bool:
        """Return whether the object is collectable.

        Returns:
            True if collectible (or storable), otherwise False.

        """
        return bool(self._is_collectable or self._is_storable)

    def get_storable(self) -> bool:
        """Return whether the object is storable.

        Returns:
            True if storable, otherwise False.

        """
        return bool(self._is_storable)

    def get_deadly(self) -> bool:
        """Return whether the object is deadly.

        Returns:
            True if deadly, otherwise False.

        """
        return bool(self._is_deadly)

    def get_pushable(self, pusher: Entity | None) -> bool:
        """Return whether the object is pushable by the given pusher.

        Args:
            pusher: The entity attempting the push; may be None.

        Returns:
            True if pushable, otherwise False.

        """
        # pusher is accepted to match the interface expected by callers.
        return bool(self._is_pushable) and (pusher or True)

    # * Complex Getters

    def in_bounds(self, r: int, c: int) -> bool:
        """Check if the given row and column are within the grid bounds.

        Args:
            r: Row index.
            c: Column index.

        Returns:
            True if [r, c] is inside the grid, False otherwise.

        """
        on_grid = self.get_on_grid()
        grid_map = on_grid.get_grid_obj_map()
        rows = len(grid_map)
        cols = len(grid_map[0]) if rows > 0 else 0
        return 0 <= r < rows and 0 <= c < cols

    def get_movement_validity(self, direction: str, r: int, c: int) -> bool:
        """Check if an Entity can move to the target coordinate.

        Args:
            direction (str): "wasd", where the Entity intends to move.
            r (int): Target row.
            c (int): Target column.

        Returns:
            True if the Entity can move to (r, c), otherwise False.

        """
        if not self.in_bounds(r, c):
            return False

        # get the object
        target_obj = self.get_obj_in_coord(r, c)

        # If there is nothing, the move is allowed.
        if target_obj is None:
            return True

        # If the target object is pushable, try to push it.
        if target_obj.get_pushable(self):
            # If the target entity cannot move, then the current entity cannot too.
            return bool(target_obj.set_pos(direction))

        # If the object is collideable, movement is blocked.
        return not target_obj.get_collideable()

    def get_entity_below(self) -> Entity | None:
        """Return the Entity that exists below this Entity in the Grid.

        Returns:
            The entity directly under this entity in the stacking order, or None.

        """
        stack = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        return stack[-2] if len(stack) > 1 else None

    # * Simple Setters

    def set_coordinate(self, r: int, c: int) -> None:
        """Set the position of this Entity. DOES NOT MODIFY THE GRID.

        Args:
            r (int): Row index.
            c (int): Column index.

        """
        self.__pos = [r, c]

    # * Complex Setters

    def set_pos(self, direction: str) -> bool:
        """Move the Entity on the Grid.

        Args:
            direction (str): The direction that the Entity wants to move.

        Returns:
            True if the move was successful, False otherwise.

        """
        r, c = self.get_pos()
        on_grid = self.get_on_grid()

        match direction.lower():
            case "w":
                r -= 1
            case "s":
                r += 1
            case "a":
                c -= 1
            case "d":
                c += 1

        if self.get_movement_validity(direction, r, c):
            on_grid.pop_layer_from_coord(*self.__pos)
            on_grid.add_layer_to_coord(r, c, self)
            self.set_coordinate(r, c)
            return True

        # The Entity failed to move (important for push logic).
        return False

    def destroy(self) -> None:
        """Destroy the Entity and remove it from the Grid.

        This removes the last occurrence of the entity from its current stack.
        """
        on_grid_stack = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        for i in range(-1, -len(on_grid_stack) - 1, -1):
            if on_grid_stack[i] == self:
                # pop_layer_from_coord expects (r, c, index)
                self.get_on_grid().pop_layer_from_coord(*self.get_pos(), i)
                break

    # * Misc functions
