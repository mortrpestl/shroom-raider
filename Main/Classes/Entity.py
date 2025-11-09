

class Entity:
    # * Attributes
    _is_collideable = (
        False  # If True, any other collideable object cannot occupy this Entity's space
    )
    _is_collectable = False  # If True, Player can collect this Entity
    _is_storable = False  # If True, then Player can keep this in inventory
    _is_pushable = False  # If True, Player can push this Entity
    _is_deadly = False  # If True, Player gets game over'd when on it.
    _is_burnable = False  # If True, triggers burning of Tree

    def __init__(self, pos: list, on_grid, ascii: str):
        self.__pos = list(pos)
        self.__on_grid = on_grid
        self.__ascii = ascii

    # * Simple Getters

    def get_ascii(self):
        return self.__ascii

    def get_on_grid(self):
        return self.__on_grid

    def get_pos(self):
        return self.__pos

    def get_obj_in_coord(self, r: int, c: int):
        return self.__on_grid.get_obj_in_coord(r, c)

    def get_burnable(self):
        return self._is_burnable

    def get_collideable(self):
        return (
            self._is_collideable or self._is_pushable
        )  # all pushables are collideable

    def get_collectable(self):
        return (
            self._is_collectable or self._is_storable
        )  # all storables are collectables

    def get_storable(self):
        return self._is_storable

    def get_deadly(self):
        return self._is_deadly

    def get_pushable(self, pusher):
        return self._is_pushable

    # * Complex Getters

    def in_bounds(self, r: int, c: int):
        on_grid = self.get_on_grid()
        rows = len(on_grid.get_grid_obj_map())
        cols = len(on_grid.get_grid_obj_map()[0])

        if (0 <= r < rows) and (0 <= c < cols):
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

        # Is the object pushable? then TRY to push that object.
        if target_obj.get_pushable(self):
            return target_obj.set_pos(
                direction
            )  # If the target entity cannot move, then the current entity cannot too.

        # Is the object collideable, otherwise? then you cannot move to that.
        elif target_obj.get_collideable():
            return False

        return True

    def get_entity_below(self):
        stack = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        return stack[-2] if len(stack) > 1 else None

    # * Simple Setters
    def set_coordinate(self, r: int, c: int):
        self.__pos = [r, c]

    # * Complex Setters

    def set_pos(self, direction: str):
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
        else:
            return False  # The Entity failed to move (important for push logic)
        return True  # The Entity has moved

    def destroy(self):
        on_grid_stck = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        for i in range(-1, -len(on_grid_stck) - 1, -1):
            if on_grid_stck[i] == self:
                self.get_on_grid().pop_layer_from_coord(*self.get_pos(), i)
                break

    # * Misc functions
