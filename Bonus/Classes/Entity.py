import Utils.sounds as s
from Classes.Entities.import_entities import import_entities
from Utils.general_utils import wait


class Entity:
    # * Attributes
    _is_collideable = False  # If True, any other collideable object cannot occupy this Entity's space
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
        if not self.get_burnable():
            raise AttributeError(f"Tried to burn unburnable object! Please implement appropriate checker")
        
        # initialization
        grid = self.get_on_grid()
        visited = set()
        curr_burn_queue = [tuple(self.get_pos())]

        # first set fire to the root node (do this, then while..)
        r, c = self.get_pos()
        self.destroy()
        visited.add((r, c))
        grid.add_active_flame(r, c)
        grid.render()
        grid.smother_active_flames()
        wait(0.125)

        # continue setting fire to the connections
        while curr_burn_queue:
            next_burn_queue = []
            for node_pos in curr_burn_queue:
                r, c = node_pos
                for delta_row, delta_column in [(1, 0), (-1, 0), (0, 1), (0, -1)]:    
                    new_row, new_column = r + delta_row, c + delta_column
                    try:
                        neighbor = grid.get_obj_in_coord(new_row, new_column)
                    except IndexError:
                        neighbor = None
                    if neighbor is not None:
                        if neighbor.get_burnable() and (new_row, new_column) not in visited:
                            next_burn_queue.append((new_row, new_column))
                            grid.add_active_flame(new_row, new_column)
                            neighbor.destroy()
                visited.add((r, c)) 
            grid.render() # only renders after the first layer is burnt
            grid.smother_active_flames() # turn active flames to smoke
            s.flamethrower_sound()
            wait(0.125)

            curr_burn_queue = list(next_burn_queue) # next LAYER to burn
        grid.clear_all_flames() # reset display

    # * Misc functions
