import os
import sys
from Classes.Entity import Entity
from Classes.Entities.import_entities import import_entities
from Utils.animator import load_in
from Utils.general_utils import clear_terminal
from Utils.Enums import DisplayMode
#from Utils.central_imports import *


class Grid:
    # * Attributes
    GRID_LIST = dict()
    EMPTY_TILES = "."  # default empty tiles

    def __init__(
        self,
        name: str,
        map_data: str,
        mode: DisplayMode = DisplayMode.EMOJI,
        metadata: dict | None = None,
    ):
        self.__name = name
        self.__player_pos = [0, 0]
        self.__total_mushrooms = 0
        self.__is_cleared = False
        self.__display_mode = mode
        self.__metadata = metadata or {}

        self.__dark_radius = self.__metadata.get("dark_radius", None)
        self.__bee_data = self.__metadata.get("bee_data", "3 3")

        # convert string to grid
        self.__grid_vis_map = [list(row) for row in map_data.strip().split("\n")]
        self.__map_rows, self.__map_cols = (
            len(self.__grid_vis_map),
            len(self.__grid_vis_map[0]),
        )
        self.__grid_obj_map = [
            [[None] for _ in range(self.__map_cols)] for _ in range(self.__map_rows)
        ]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

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
        self.character_mapping = {  # for ENTITY display
            self.ENTITIES["Player"]: ("🧑", "L"),
            self.ENTITIES["Tree"]: ("🌲", "T"),
            self.ENTITIES["Mushroom"]: ("🍄", "+"),
            self.ENTITIES["Rock"]: ("🗿", "R"), #"🪨"
            self.ENTITIES["Water"]: ("🟦", "~"),
            self.ENTITIES["PavedTile"]: ("⬜", "_"),
            self.ENTITIES["Axe"]: ("🪓", "x"),
            self.ENTITIES["Flamethrower"]: ("🔥", "*"),
            self.ENTITIES["Flash"]: ("✨", "?"),
            self.ENTITIES["Bomb"]: ("💣", "!"),
            self.ENTITIES["Beehive"]: ("🍯", "&"),
            self.ENTITIES["Bee"]: ("🐝", ">"),
            self.ENTITIES["Ice"]: ("🧊", "#"),
            self.ENTITIES["Log"]: ("📦", "o"),
        }
        self.overlay_mapping = {  # for NON-ENTITY display, dubbed "overlay"
            "Flame": ("🔥", "&"),
            "Smoke": ("⚫", "0"),
            "Darkness": ("⬛", "#"),
            "Blast": ("💥", "X"),
        }
        # NOTE since non-entity display is separate, these can have the same display string as entity displays
        self.initialization_map = {
            k[1]: (v, k[0]) for v, k in self.character_mapping.items()
        }

        self.__active_flashes = []  # flashes affect darkness only
        self.__active_flames = set()  # for flamethrower animation
        self.__active_smokes = set()  # for leftover smoke
        self.__active_blasts = set()  # for bombs

        # initialize objects in grid
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], [r, c])
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        Grid.GRID_LIST[name] = self

    # * Simple Getters

    def get_player(self):
        return self.get_obj_in_coord(*self.__player_pos)

    def get_player_pos(self):
        return self.__player_pos

    def get_grid_obj_map(self):
        return self.__grid_obj_map

    def get_grid_user_display(self, r: int, c: int):
        return self.__grid_user_display[r][c]

    def get_overlay_of_symbol(self, symbol: str):
        offset = self.get_display_mode().value
        return self.overlay_mapping[symbol][offset]

    def get_layers_from_coord(self, r: int, c: int):
        return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self):
        return self.__total_mushrooms

    def increment_total_mushrooms(self):
        self.__total_mushrooms += 1

    def get_dark_radius(self):
        return self.__dark_radius

    def get_bee_data(self):
        return self.__bee_data

    def get_is_cleared(self):
        return self.__is_cleared

    def get_active_flashes(self):
        return self.__active_flashes

    def get_active_flames(self):
        return self.__active_flames

    def get_active_smokes(self):
        return self.__active_smokes

    def get_active_blasts(self):
        return self.__active_blasts

    def get_display_mode(self):
        return self.__display_mode

    def get_metadata(self):
        return self.__metadata

    @staticmethod
    def get_grid_by_name(name: str):
        if name not in Grid.GRID_LIST:
            raise KeyError(f"No grid found with name: {name}")
        return Grid.GRID_LIST[name]

    # * Complex Getters
    def pop_layer_from_coord(self, r: int, c: int, layer: int = -1):
        return self.get_grid_obj_map()[r][c].pop(layer)

    # use sparingly
    def push_layer_to_coord(self, r: int, c: int, entity: Entity, layer: int = -1):
        return self.get_grid_obj_map()[r][c].append(entity)

    def get_obj_in_coord(self, r: int, c: int, layer: int = -1):
        if not (0 <= r < self.__map_rows and 0 <= c < self.__map_cols):
            raise IndexError(f"coordinate {r, c} out of bounds")

        return self.__grid_obj_map[r][c][layer]

    def get_display_symbol_of_obj(self, obj: Entity | None):
        offset = self.get_display_mode().value
        return self.character_mapping[type(obj)][offset]

    # * Simple Setters
    def level_clear(self):
        self.__is_cleared = True

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

    def set_player_pos(self, pos: list[int]):
        self.__player_pos = pos

    def set_display_in_coord(self, r: int, c: int, symbol: str):
        self.__grid_user_display[r][c] = symbol

    # * Complex Setters
    def add_layer_to_coord(self, r: int, c: int, entity: Entity):
        self.get_grid_obj_map()[r][c].append(entity)

    # * Misc
    def init_coord(self, symbol: str, coord: list):
        if symbol in Grid.EMPTY_TILES:
            return None, "　"
        if symbol == "L":
            self.set_player_pos(coord)
        if symbol == "+":
            self.increment_total_mushrooms()

        item = self.initialization_map.get(symbol)

        if not item:
            raise ValueError(f"Unknown type symbol: {symbol}")

        item_type, item_display_value = item

        # * CHECK METADATA ASSOCIATIONS

        if symbol == "&":
            bee_lag, bee_count = map(int, self.__bee_data.split())
            return item_type(
                coord, self, bee_lag=bee_lag, bee_count=bee_count
            ), item_display_value

        return item_type(coord, self, symbol), item_display_value

    # * Flash / Darkness Setters
    def register_flash(self, flash: Entity):
        if flash not in self.__active_flashes:
            self.__active_flashes.append(flash)

    def update_all_flashes(self):
        for flash in self.__active_flashes:
            flash.update_radius()
            if flash.get_radius() <= 0:
                self.__active_flashes.remove(flash)

    # * Bee Updaters

    def update_all_bees(self):
        BEE = self.ENTITIES["Bee"]
        BEE.update_all()

    # * Visualization Helpers
    def __compute_display_for_cell(self, r: int, c: int, obj: Entity | None):
        display = self.get_display_symbol_of_obj(obj) if obj else "　"

        dark_radius = self.get_dark_radius()

        # * FLAME LOGIC
        # Note that whenever tree burns: 1.) it adds an active flame pos; 2.) sets its former pos to flame.
        if (r, c) in self.get_active_flames():
            display = self.get_overlay_of_symbol("Flame")

        # * BLAST LOGIC
        if (r, c) in self.get_active_blasts():
            display = self.get_overlay_of_symbol("Blast")

        # * SMOKE RESIDUE LOGIC
        if (r, c) in self.get_active_smokes():
            display = self.get_overlay_of_symbol("Smoke")

        # skip darkness logic if no dark_radius
        if dark_radius is None:
            return display

        # * DARKNESS LOGIC
        # lit by flash? then display object
        if any(
            abs(fl.get_pos()[0] - r) + abs(fl.get_pos()[1] - c) <= fl.get_radius()
            for fl in self.get_active_flashes()
        ):
            return display

        # darken if dark_radius is set and outside radius
        distance = abs(self.get_player_pos()[0] - r) + abs(self.get_player_pos()[1] - c)
        if distance > dark_radius:
            display = self.get_overlay_of_symbol("Darkness")

        return display

    def visualize_map(self):
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj = self.get_obj_in_coord(r, c)
                self.__grid_user_display[r][c] = self.__compute_display_for_cell(
                    r, c, obj
                )

    def get_vis_map_as_str(self):
        self.visualize_map()
        return "\n".join("".join(row) for row in self.__grid_user_display)

    def render(self, test_mode: bool = False, f=False):
        p = self.get_player()
        self.update_all_flashes()
        self.update_all_bees()

        total_mushrooms = self.get_total_mushrooms()
        mushrooms_collected = p.get_mushroom_count()
        item_here = p.get_entity_below()  # element below player
        held_item = p.get_item()

        win, lose = (mushrooms_collected == total_mushrooms), p.get_is_dead()

        self.visualize_map()

        display = []  # FINAL DISPLAY INITIALIZATION

        os.system("cls" if os.name == "nt" else "clear")

        # * GRID DISPLAY
        for row in self.__grid_user_display:
            display.append("".join(row))

        display.append(
            f"\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected"
        )
        if win:
            display.append("You win!")
        if lose:
            display.append("You lose...")

        # * CONTEXTUAL DISPLAYS
        item_here_display = "- Nothing Here!"
        held_item_display = "- Not holding anything..."
        additional_inputs = []

        if item_here is not None:
            symbol = self.get_display_symbol_of_obj(item_here)
            additional_inputs.append(f"\n[p] Pick up [{symbol}{item_here}]?")

            item_here_display = (
                f"[{self.get_display_symbol_of_obj(item_here)}{item_here}] is here"
            )

        if p.get_item() is not None:
            if p.get_item().get_passive():
                symbol = self.get_display_symbol_of_obj(p.get_item())
                additional_inputs.append(
                    f"\n[F] Use passive item [{symbol}{p.get_item()}]"
                )

        additional_inputs = "".join(additional_inputs)

        if held_item is not None:
            held_item_display = (
                f"Holding item [{self.get_display_symbol_of_obj(held_item)}{held_item}]"
            )

        # * PLAYER "HUD"
        if not win and not lose:
            terminal_gui = f"""
[w] Move up   
[a] Move left 
[s] Move down 
[d] Move right{additional_inputs}
[Q] Quit level
[!] Reset     

{item_here_display}
{held_item_display}

What will you do? """

            display.append(terminal_gui)
            clear_terminal()
            if (
                f
            ):  # if it is the FIRST time render is called, then animate the loading in!
                load_in("\n".join(display), 5)
            else:
                print((center_wr_to_terminal_size("\n".join(display))))
            sys.stdout.flush()

        return win or lose
