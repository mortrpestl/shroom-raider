import sys

from Classes.Entities.import_entities import import_entities
from Classes.Entity import Entity
from colorama import Back, Fore, Style
from Utils.animator import load_in
from Utils.Enums import DisplayMode
from Utils.general_utils import center_wr_to_terminal_size, clear_terminal
from wcwidth import wcswidth


class Grid:
    """The grid is the playarea in which the players and all game objects reside

    It is represented as a 3D data structure, a 2D list with each coordinate containing a stack of entities

    Attributes:
        GRID_LIST: A dictionary of all grid objects created

        __name: The name of a Grid object
        __player_pos: The player position within a certain Grid object
        __total_mushrooms: Number of mushrooms contained in a grid
        __is_cleared: Indicates if a certain Grid has been cleared or not
        __display_mode: The display mode of the Grid
        __metadata: Contains data on darkness and Bees
        __dark_radius, __bee_data: Contained in metadata. Indicates how to handle level darkness and bee behaviors

        __grid_vis_map: 2D list of characters that represent the Grid
        __map_rows, __map_cols: The number of rows and columns that the Grid contains
        __grid_obj_map: A 3D data structure containing all the objects in the Grid
        __grid_user_display: A 2D list containing the visualization of the Grid to be shown to users
        __grid_color_display: A colored version of grid_user_display
        __ENTITIES: A dictionary containing all possible entities that could reside in the Grid

        __character_mapping: Maps each entity to their visual representation
        overlay_mapping: The overlays used for the animation effects
        __initialization_map: Maps each valid character to their corresponding object and visual representation

        __active_flashes, __active_flames, __active_smokes, __active_blasts: Used to store frames for animations

    """

    GRID_LIST = dict()
    EMPTY_TILES = "."  # default empty tiles

    def __init__(
        self,
        name: str,
        map_data: str,
        mode: DisplayMode = DisplayMode.EMOJI,
        metadata: dict | None = None,
    ):
        """Initializes a Grid object based on a given stage

        Args:
            name: The name of the Grid
            map_data: A string representation of the stage
            mode: The displaymode of the grid
            metadata: Data concerning darkness and bees

        """
        self.__name = name
        self.__player_pos = [0, 0]
        self.__total_mushrooms = 0
        self.__is_cleared = False
        self.__display_mode = mode
        self.__metadata = metadata or {}

        self.__dark_radius = self.__metadata.get("dark_radius", None)
        self.__bee_data = self.__metadata.get("bee_data", "3 3")
        self.__song_name = self.__metadata.get("song_name")

        # convert string to grid
        self.__grid_vis_map = [list(row) for row in map_data.strip().split("\n")]
        self.__map_rows, self.__map_cols = (
            len(self.__grid_vis_map),
            len(self.__grid_vis_map[0]),
        )
        self.__grid_obj_map = [[[None] for _ in range(self.__map_cols)] for _ in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]
        self.__grid_color_display = [[] for _ in range(self.__map_rows)]

        self.ENTITIES = import_entities({
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
        })
        self.character_mapping = {  # for ENTITY display
            self.ENTITIES["Player"]: (("🧑", "L"), Back.GREEN),
            self.ENTITIES["Tree"]: (("🌲", "T"), Back.GREEN),
            self.ENTITIES["Mushroom"]: (("🍄", "+"), Back.GREEN),
            self.ENTITIES["Rock"]: (("🗿", "R"), Back.GREEN),
            self.ENTITIES["Water"]: (("🟦", "~"), Back.BLUE),
            self.ENTITIES["PavedTile"]: (("⬜", "_"), Back.WHITE + Fore.WHITE),
            self.ENTITIES["Axe"]: (("🪓", "x"), Back.GREEN),
            self.ENTITIES["Flamethrower"]: (("🔥", "*"), Back.GREEN),
            self.ENTITIES["Flash"]: (("✨", "?"), Back.GREEN),
            self.ENTITIES["Bomb"]: (("💣", "!"), Back.GREEN),
            self.ENTITIES["Beehive"]: (("🍯", "&"), Back.GREEN),
            self.ENTITIES["Bee"]: (("🐝", ">"), Back.GREEN),
            self.ENTITIES["Ice"]: (("🧊", "#"), Back.CYAN),
            self.ENTITIES["Log"]: (("📦", "o"), Back.GREEN),
        }
        self.overlay_mapping = {  # for NON-ENTITY display, dubbed "overlay"
            "Flame": (("🔥", "&"), Back.YELLOW),
            "Smoke": (("⚫", "0"), Back.BLACK + Fore.BLACK),
            "Darkness": (("⬛", "#"), Back.BLACK + Fore.BLACK),
            "Blast": (("💥", "X"), Back.GREEN),
        }
        # NOTE since non-entity display is separate, these can have the same display string as entity displays
        self.initialization_map = {k[0][1]: (v, k[0][0], k[1]) for v, k in self.character_mapping.items()}

        self.__active_flashes = []  # flashes affect darkness only
        self.__active_flames = set()  # for flamethrower animation
        self.__active_smokes = set()  # for leftover smoke
        self.__active_blasts = set()  # for bombs

        # initialize objects in grid
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display, color = self.init_coord(self.__grid_vis_map[r][c], [r, c])
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)
                self.__grid_color_display[r].append(color)

        Grid.GRID_LIST[name] = self

    # * Simple Getters

    def get_player(self):
        """Returns: The Player entity on the Grid"""
        return self.get_obj_in_coord(*self.__player_pos)

    def get_player_pos(self):
        """Returns: The Player entity's position on the Grid"""
        return self.__player_pos

    def get_grid_obj_map(self):
        """Returns: A 2-D list of stacks, representing each tile on the Grid and the entities they contain"""
        return self.__grid_obj_map

    def get_grid_user_display(self, r: int, c: int):
        """Args:
            r, c: The row and column coordinate of the cell being accessed

        Returns:
            The user display for that cell

        """
        return self.__grid_user_display[r][c]

    def get_grid_color_map(self):
        """Returns: The color display for the grid"""
        return self.__grid_color_display

    def get_layers_from_coord(self, r: int, c: int):
        """Returns: The stack of a certain coordinate, containing the entities at that coordinate"""
        return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self):
        """Returns: The integer amount of total mushrooms contained in the Grid"""
        return self.__total_mushrooms

    def get_dark_radius(self):
        """Returns: The size of the visible section for a given Grid"""
        return self.__dark_radius

    def get_bee_data(self):
        """Returns: The lag and count of bees for this Grid"""
        return self.__bee_data

    def get_is_cleared(self):
        """Returns: A boolean indicating if the current Grid has been cleared"""
        return self.__is_cleared

    def get_display_mode(self):
        """Returns: The display mode of the current Grid"""
        return self.__display_mode

    def get_metadata(self):
        """Returns: The metadata of the current Grid"""
        return self.__metadata

    def get_active_flashes(self):
        """Used for animation"""
        return self.__active_flashes

    def get_active_flames(self):
        """Used for animation"""
        return self.__active_flames

    def get_active_smokes(self):
        """Used for animation"""
        return self.__active_smokes

    def get_active_blasts(self):
        """Used for animation"""
        return self.__active_blasts

    def get_song_name(self):
        """Used for displaying song name"""
        return self.__song_name

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
            raise KeyError(f"No grid found with name: {name}")
        return Grid.GRID_LIST[name]

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

    # use sparingly
    def push_layer_to_coord(self, r: int, c: int, entity: Entity, layer: int = -1):
        """Adds an entity to the Grid at a certain coordinate

        Args:
            r: The row being accessed
            c: The column being accessed
            obj: The entity being added to the coordinate
            layer: The layer that the entity is being added to

        """
        return self.get_grid_obj_map()[r][c].append(entity)

    def get_obj_in_coord(self, r: int, c: int, layer: int = -1):
        """Gets the object at a certain coordinate and layer

        Args:
            r, c: The coordinate being accessed
            layer: The layer of that coordinate being accessed

        Returns:
            The object at that coordinate

        Raises:
            IndexError: If the coordinate is out of Grid bounds

        """
        if not (0 <= r < self.__map_rows and 0 <= c < self.__map_cols):
            raise IndexError(f"coordinate {r, c} out of bounds")

        return self.__grid_obj_map[r][c][layer]

    def get_display_of_obj(self, obj: Entity | None | str):
        """Gets the display representation of an object

        Args:
            obj: The given object

        Returns:
            The display symbol of the object

        """
        offset = self.get_display_mode().value
        if isinstance(obj, Entity):
            values = self.character_mapping[type(obj)]
        if isinstance(obj, str):
            values = self.overlay_mapping[obj]
        # return symbol and color
        return {"symbol": values[0][offset], "color": values[1]}

    # * Simple Setters
    def level_clear(self):
        """Sets the current level as completed/cleared"""
        self.__is_cleared = True

    def increment_total_mushrooms(self):
        """Increments total mushrooms collected by one"""
        self.__total_mushrooms += 1

    def set_player_pos(self, pos: list[int]):
        """Sets the player position

        Args:
            pos: The position of the player

        """
        self.__player_pos = pos

    def set_display_in_coord(self, r: int, c: int, symbol: str):
        """Sets the display symbol of a coordinate

        Args:
            r, c: The coordinate being accessed
            symbol: The symbol to be set

        """
        self.__grid_user_display[r][c] = symbol

    def set_color_in_coord(self, r: int, c: int, color: str):
        """Sets the display color of a coordinate

        Args:
            r, c: The coordinate being accessed
            color: The color of the coordinate

        """
        self.__grid_color_display[r][c] = color

    """The next few functions are for animation use only"""

    def add_active_flame(self, r, c):
        self.__active_flames.add((r, c))

    def add_active_blast(self, r, c):
        self.__active_blasts.add((r, c))

    def smother_active_flames(self):
        self.__active_smokes = self.__active_smokes | self.__active_flames
        self.__active_flames = set()

    def smother_active_blasts(self):
        self.__active_smokes = self.__active_smokes | self.__active_blasts
        self.__active_blasts = set()

    def clear_all_smoke(self):
        self.__active_smokes = set()

    def clear_all_blasts(self):
        self.clear_all_smoke()
        self.__active_blasts = set()

    def clear_all_flames(self):
        self.clear_all_smoke()
        self.__active_flames = set()

    # * Complex Setters
    def add_layer_to_coord(self, r: int, c: int, entity: Entity):
        """Adds an entity to the Grid at a certain coordinate

        Args:
            r: The row being accessed
            c: The column being accessed
            obj: The entity being added to the coordinate

        """
        self.get_grid_obj_map()[r][c].append(entity)

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
        if symbol in Grid.EMPTY_TILES:
            return None, "　", Back.GREEN
        if symbol == "L":
            self.set_player_pos(coord)
        if symbol == "+":
            self.increment_total_mushrooms()

        item = self.initialization_map.get(symbol)

        if not item:
            raise ValueError(f"Unknown type symbol: {symbol}")

        item_type, item_display_value, item_color = item

        # * CHECK METADATA ASSOCIATIONS

        if symbol == "&":
            bee_lag, bee_count = map(int, self.__bee_data.split())
            return item_type(coord, self, bee_lag=bee_lag, bee_count=bee_count), item_display_value, item_color

        return item_type(coord, self, symbol), item_display_value, item_color

    # * Flash / Darkness Setters
    def register_flash(self, flash: Entity):
        """Activates a current flash

        Args:
            flash: The flash being accessed

        """
        if flash not in self.__active_flashes:
            self.__active_flashes.append(flash)

    def update_all_flashes(self):
        """Updates the flash display"""
        for flash in self.__active_flashes:
            flash.update_radius()
            if flash.get_radius() <= 0:
                self.__active_flashes.remove(flash)

    # * Bee Updaters

    def update_all_bees(self):
        """Updates all bees in Grid"""
        BEE = self.ENTITIES["Bee"]
        BEE.update_all()

    # * Visualization Helpers
    def __compute_display_for_cell(self, r: int, c: int, obj: Entity | None):
        """Computes the display and color of a cell

        Args:
            r, c: The coordinate of the cell
            obj: The topmost Entity at that cell

        Returns:
            The display of the object at the cell, and the color of the cell

        """
        display, color = list(self.get_display_of_obj(obj).values()) if obj else ["　", Back.GREEN]

        dark_radius = self.get_dark_radius()

        # * FLAME LOGIC
        # Note that whenever tree burns: 1.) it adds an active flame pos; 2.) sets its former pos to flame.
        if (r, c) in self.get_active_flames():
            display, color = list(self.get_display_of_obj("Flame").values())

        # * BLAST LOGIC
        if (r, c) in self.get_active_blasts():
            display, color = list(self.get_display_of_obj("Blast").values())

        # * SMOKE RESIDUE LOGIC
        if (r, c) in self.get_active_smokes():
            display, color = list(self.get_display_of_obj("Smoke").values())

        # skip darkness logic if no dark_radius
        if dark_radius is None:
            return display, color

        # * DARKNESS LOGIC
        # lit by flash? then display object
        if any(
            abs(fl.get_pos()[0] - r) + abs(fl.get_pos()[1] - c) <= fl.get_radius() for fl in self.get_active_flashes()
        ):
            return display, color

        # darken if dark_radius is set and outside radius
        distance = abs(self.get_player_pos()[0] - r) + abs(self.get_player_pos()[1] - c)
        if distance > dark_radius:
            display, color = list(self.get_display_of_obj("Darkness").values())

        return display, color

    def visualize_map(self):
        """Creates the user-facing visualization of the Grid

        Args:
            mode: Indicates how the visualization should be formatted

        """
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj = self.get_obj_in_coord(r, c)
                self.__grid_user_display[r][c], self.__grid_color_display[r][c] = self.__compute_display_for_cell(
                    r,
                    c,
                    obj,
                )

    def get_vis_map_as_str(self):
        """Gets the visualization map of the Grid

        Args:
            mode: Indicates how the visualization should be formatted

        Returns:
            A multi-line string representation of the Grid based on the given mode

        """
        self.visualize_map()
        return "\n".join("".join(row) for row in self.__grid_user_display)

    def render(self, test_mode: bool = False, f: bool = False):
        """Prints the Grid and GUI for the user

        Args:
            test_mode: Indicates if the game should be printed in debugging mode
            f: Flag indicating if this is first time Grid has been rendered
        Returns:
            A boolean indicating if the game has ended

        """
        p = self.get_player()
        self.update_all_flashes()
        self.update_all_bees()

        total_mushrooms = self.get_total_mushrooms()
        mushrooms_collected = p.get_mushroom_count()
        item_here = p.get_entity_below()  # element below player
        held_item = p.get_item()

        win, lose = (mushrooms_collected == total_mushrooms), p.get_is_dead()

        self.visualize_map()

        # * INITIALIZATION OF DISPLAY VALUES
        title_display = []
        grid_display = []
        hud_display = []
        # NOTE grid_display is separate to "bypass" weirdness from ANSI

        # * TITLE DISPLAY
        span = max((wcswidth("".join(self.__grid_user_display[0])) - 3) // 4, 1)
        spanner = f"{Fore.GREEN}\nx{'-' * span}{'=' * span}{{🍄}}{'=' * span}{'-' * span}x\n{Style.RESET_ALL}"
        with open("Assets/UI/GameProperArt.txt", encoding="utf+8") as art:
            title_display.append(f"{Fore.RED}\n{art.read()}\n{Style.RESET_ALL}")
            title_display.append(spanner)

        # * GRID DISPLAY
        grid_display = []
        for row in self.__grid_user_display:
            grid_display.append("".join(row))

        # * CONTEXTUAL DISPLAYS (in HUD)
        item_here_display = "- Nothing Here!"
        held_item_display = "- Not holding anything..."
        additional_inputs = []

        if item_here is not None:
            symbol = self.get_display_of_obj(item_here)["symbol"]
            if item_here.get_collectable():
                additional_inputs.append(f"\n[p] Pick up [{symbol} {item_here}]?")
            item_here_display = f"[{symbol} {item_here}] is here"

        if p.get_item() is not None:
            if p.get_item().get_passive():
                symbol = self.get_display_of_obj(p.get_item())["symbol"]
                additional_inputs.append(f"\n[F] Use passive item [{symbol} {p.get_item()}]")

        additional_inputs = "".join(additional_inputs)

        if held_item is not None:
            held_item_display = f"Holding item [{self.get_display_of_obj(held_item)['symbol']}{held_item}]"

        # * PLAYER "HUD"
        terminal_gui = f"""
[w] Move up
[a] Move left
[s] Move down
[d] Move right{additional_inputs}
[Q] Quit level
[!] Reset

{item_here_display}
{held_item_display}

Song Playing: {self.get_song_name()}

What will you do? """

        hud_display.append(spanner)
        hud_display.append(f"\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected")
        if win:
            hud_display.append("You win!")
        if lose:
            hud_display.append("You lose...")

        hud_display.append(terminal_gui)

        # * PROCESS DISPLAYS

        clear_terminal()
        if f:  # if it is the FIRST time render is called, then animate the loading in!
            load_in("\n".join(title_display), 1, centered=True)  # colors initialized before
            load_in(
                "\n".join(grid_display),
                1,
                centered=True,
                colors=self.get_grid_color_map(),
                colors2=[Fore.GREEN],
                mode="--grid",
            )
            load_in("\n".join(hud_display), 1, centered=True)
        else:
            print(center_wr_to_terminal_size("\n".join(title_display)))  # colors initialized before
            print(center_wr_to_terminal_size("\n".join(grid_display), colors=self.get_grid_color_map(), grid_mode=True))
            print(center_wr_to_terminal_size("\n".join(hud_display)))
        sys.stdout.flush()

        return win or lose
