import os
from Classes.Entity import Entity
from Classes.Entities.import_entities import import_entities


class Grid:
    """
    The grid is the playarea in which the players and all game objects reside

    It is represented as a 3D data structure, a 2D list with each coordinate containing a stack of entities

    Attributes:
        GRID_LIST: A dictionary of all grid objects created

        __name: The name of a Grid object
        __player_pos: The player position within a certain Grid object
        __total_mushrooms: Number of mushrooms contained in a grid
        __is_cleared: Indicates if a certain Grid has been cleared or not
        __grid_vis_map: 2D list of characters that represent the Grid
        __map_rows, __map_cols: The number of rows and columns that the Grid contains
        __grid_obj_map: A 3D data structure containing all the objects in the Grid
        __grid_user_display: A 2D list containing the visualization of the Grid to be shown to users
        __ENTITIES: A dictionary containing all possible entities that could reside in the Grid

        __character_mapping: Maps each entity to their visual representation
        __initialization_map: Maps each valid character to their corresponding object and visual representation
    """

    # * Attributes
    GRID_LIST = dict()  # Dictionary of all grid objects created

    def __init__(self, name: str, map_data: str):
        """Initializes a Grid object based on a given stage

        Args:
            name: The name of the Grid
            map_data: A string representation of the stage
        """
        self.__name = name
        self.__player_pos = [0, 0]
        self.__total_mushrooms = 0
        self.__is_cleared = False

        self.__grid_vis_map = [list(rows) for rows in map_data.strip().split("\n")]
        self.__map_rows, self.__map_cols = (
            len(self.__grid_vis_map),
            len(self.__grid_vis_map[0]),
        )
        self.__grid_obj_map = [[[None] for c in range(self.__map_cols)] for r in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

        self.ENTITIES = import_entities({
            "Player",
            "Tree",
            "Rock",
            "Mushroom",
            "Water",
            "PavedTile",
            "Axe",
            "Flamethrower",
        })
        self.character_mapping = {  # for display
            self.ENTITIES["Player"]: ("🧑", "L"),
            self.ENTITIES["Tree"]: ("🌲", "T"),
            self.ENTITIES["Mushroom"]: ("🍄", "+"),
            self.ENTITIES["Rock"]: ("🪨 ", "R"),
            self.ENTITIES["Water"]: ("🟦", "~"),
            self.ENTITIES["PavedTile"]: ("⬜", "_"),
            self.ENTITIES["Axe"]: ("🪓", "x"),
            self.ENTITIES["Flamethrower"]: ("🔥", "*"),
        }
        self.initialization_map = {k[1]: (v, k[0]) for v, k in self.character_mapping.items()}

        # initialize all items and makes object map for collision detection
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], [r, c])
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        Grid.GRID_LIST[self.__name] = self

    # * Simple Getters

    def get_player(self):
        """
        Returns: The Player entity on the Grid
        """
        return self.get_obj_in_coord(*self.__player_pos)

    def get_grid_obj_map(self):
        """
        Returns: A 2-D list of stacks, representing each tile on the Grid and the entities they contain
        """
        return self.__grid_obj_map

    def get_layers_from_coord(self, r: int, c: int):
        """
        Returns: The stack of a certain coordinate, containing the entities at that coordinate
        """
        return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self):
        """
        Returns: The integer amount of total mushrooms contained in the Grid
        """
        return self.__total_mushrooms

    def get_is_cleared(self):
        """
        Returns: A boolean indicating if the current Grid has been cleared
        """
        return self.__is_cleared

    # * Complex Getters

    def pop_layer_from_coord(self, r: int, c: int, layer: int = -1):
        """Removes an entity at a certain coordinate.

        Args:
            r: The row being accessed
            c: The column being accessed
            layer: The layer of the stack in which the entity is located

        Returns: An entity or None
        """
        return self.get_grid_obj_map()[r][c].pop(layer)

    @staticmethod
    def get_grid_by_name(name: str):
        """Gets a Grid object based on name

        Args:
            name: the name of the Grid being accessed

        Returns:
            A grid object

        Raises:
            KeyError: If no Grid with the given name exists

        """
        if name not in Grid.GRID_LIST:
            raise KeyError(f"No grid found with name:{name}")
        return Grid.GRID_LIST[name]

    def get_obj_in_coord(self, r: int, c: int, layer: int = -1):
        if not (0 <= r < self.__map_rows and 0 <= c < self.__map_cols):
            raise IndexError(f"coordinate {r, c} out of bounds")

        return self.__grid_obj_map[r][c][layer]

    def get_display_symbol_of_obj(self, obj: Entity | None, mode: str = "emoji"):
        if mode == "emoji":
            offset = 0
        else:
            offset = 1

        for cm in self.character_mapping:
            if isinstance(obj, cm):
                return self.character_mapping[cm][offset]

    # * Simple Setters

    def level_clear(self):
        """Sets the current level as completed/cleared"""
        self.__is_cleared = True

    def increment_total_mushrooms(self):
        """Increments total mushrooms collected by one"""
        self.__total_mushrooms += 1

    # * Complex Setters

    def add_layer_to_coord(self, r: int, c: int, obj: Entity | None):
        """Adds an entity to the Grid at a certain coordinate

        Args:
            r: The row being accessed
            c: The column being accessed
            obj: The entity being added to the coordinate
        """
        self.get_grid_obj_map()[r][c].append(obj)

    # * Misc

    def init_coord(self, symbol: str, coord: list):
        """Initializes a Grid coordinate based on a character from the stage string

        Args:
            symbol: The character being processed
            coord: [r, c]
                r: The row being accessed
                c: The column being accessed

        Returns:
            The object to be placed in the Grid and the display character for that entity

        Raises:
            ValueError: If the given symbol is not a valid symbol
        """
        if symbol == ".":
            return None, "　"
        if symbol == "L":
            self.__player_pos = coord
        if symbol == "+":
            self.increment_total_mushrooms()

        item = self.initialization_map.get(symbol)

        if not item:
            raise ValueError(f"Unknown type symbol: {symbol}")

        item_type, item_display_value = item

        return item_type(coord, self, symbol), item_display_value

    def visualize_map(self, mode: str = "emoji"):
        """Creates the user-facing visualization of the Grid

        Args:
            mode: Indicates how the visualization should be formatted
        """
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj_in_coord = self.get_obj_in_coord(r, c)

                if not obj_in_coord:
                    self.__grid_user_display[r][c] = "　" if mode == "emoji" else "."
                else:
                    self.__grid_user_display[r][c] = self.get_display_symbol_of_obj(obj_in_coord, mode)

    def get_vis_map_as_str(self, mode: str = "ascii"):
        """Gets the visualization map of the Grid

        Args:
            mode: Indicates how the visualization should be formatted

        Returns:
            A multi-line string representation of the Grid based on the given mode
        """
        grid_str_rep = []

        self.visualize_map(mode)

        for row in self.__grid_user_display:
            grid_str_rep.append("".join(row))

        return "\n".join(grid_str_rep)

    def render(self, p: Entity, test_mode: bool = False):
        """Prints the Grid and GUI for the user

        Args:
            p: The Player entity
            test_mode: Indicates if the game should be printed in debugging mode

        Returns:
            A boolean indicating if the game has ended
        """
        total_mushrooms = self.get_total_mushrooms()
        mushrooms_collected = p.get_mushroom_count()
        item_here = p.get_entity_below().__class__.__name__  # element below player
        held_item = p.get_item().__class__.__name__

        win = mushrooms_collected == total_mushrooms
        lose = p.get_is_dead()

        self.visualize_map()

        os.system("cls" if os.name == "nt" else "clear")
        for row in self.__grid_user_display:
            print("".join(row))

        print(f"\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected")

        if win:
            print("You win!")
        elif lose:
            print("You lose...")

        else:
            terminal_gui = f"""
[W] Move up
[A] Move left
[S] Move down
[D] Move right
[!] Reset

{item_here + " is here" if item_here != "NoneType" else "Nothing Here"}
{f"Holding item {held_item}" if held_item != "NoneType" else "Not holding anything"}

What will you do?
            """
            print(terminal_gui, end="")

        return win or lose
