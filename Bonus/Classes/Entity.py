import Utils.sounds as s
from Classes.Entities.import_entities import import_entities
from Utils.general_utils import wait


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
    _is_passive = False  # If True, affects the map in some way without having to be directly used on another object
    _is_tile_trigger = False  # If True, entity triggers game event when stepped on
    _is_explodable = False  # If True, can be exploded with bomb

    def __init__(self, pos: list, on_grid, ascii: str):
        self.__pos = list(pos)
        self.__on_grid = on_grid
        self.__ascii = ascii
        self.ENTITIES = import_entities(
            {
                "Player",
                "Tree",
                "Rock",
                "Mushroom",
                "Water",
                "PavedTile",
                "Axe",
                "Flamethrower",
                "Flash",
                "Bomb",
                "Beehive",
                "Bee",
                "Ice",
                "Log",
            }
        )

    # * Simple Getters

    def __repr__(self):
        return self.__class__.__name__

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

    def get_tile_trigger(self):
        return self._is_tile_trigger

    def get_explodable(self):
        return self._is_explodable

    def get_deadly(self):
        return self._is_deadly

    def get_pushable(self, pusher):
        return self._is_pushable

    def get_passive(self):
        return self._is_passive

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

        is_player = owns_flamethrower = target_is_log = False
        target_is_log = isinstance(target_obj, self.ENTITIES["Log"])
        is_player = isinstance(self, self.ENTITIES["Player"])

        if is_player:
            owns_flamethrower = isinstance(
                self.get_item(), self.ENTITIES["Flamethrower"]
            )

        burn_log = target_is_log and owns_flamethrower

        # Is the object pushable? then TRY to push that object.
        if target_obj.get_pushable(self) and not burn_log:
            return target_obj.set_pos(
                direction
            )  # If the target entity cannot move, then the current entity cannot too.

        # Is the object collideable, otherwise? then you cannot move to that.
        elif target_obj.get_collideable() and not burn_log:
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
            s.failpush_sound()
            return False  # The Entity failed to move (important for push logic)
        return True  # The Entity has moved

    def destroy(self):
        on_grid_stck = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        for i in range(-1, -len(on_grid_stck) - 1, -1):
            if on_grid_stck[i] == self:
                self.get_on_grid().pop_layer_from_coord(*self.get_pos(), i)
                break

    def burn_connected(self, visited: set | None = None):
        if visited is None:
            visited = set()

        grid = self.get_on_grid()
        obj_map = grid.get_grid_obj_map()

        r, c = self.get_pos()
        visited.add((r, c))
        self.destroy()
        grid.set_display_in_coord(
            *self.get_pos(), "🔥" if grid.get_display_mode() == "emoji" else "&"
        )
        grid.render()
        wait(0.075)
        s.flamethrower_sound()
        grid.add_active_flame(*self.get_pos())
        wait(0.075)

        for delta_row, delta_column in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_row, new_column = r + delta_row, c + delta_column

            if 0 <= new_row < len(obj_map) and 0 <= new_column < len(obj_map[0]):
                neighbor = obj_map[new_row][new_column][-1]
                if (
                    isinstance(neighbor, (self.ENTITIES["Tree"], self.ENTITIES["Log"]))
                    and (new_row, new_column) not in visited
                ):
                    neighbor.burn_connected(visited)

    # * Misc functions
