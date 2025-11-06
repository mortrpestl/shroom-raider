import os
from Classes.Entities.import_entities import import_entities

class Grid:
    # * Attributes
    GRID_LIST = dict()
    EMPTY_TILES = '.'  # default empty tiles

    def __init__(self, name: str, map_data: str, dark_radius: int | None = None):
        self.__name = name
        self.__player_pos = [0, 0]
        self.__total_mushrooms = 0
        self.__is_cleared = False
        self._dark_radius = dark_radius

        # convert string to grid
        self.__grid_vis_map = [list(row) for row in map_data.strip().split('\n')]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        self.__grid_obj_map = [[[None] for _ in range(self.__map_cols)] for _ in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

        self.ENTITIES = import_entities({
            "Player", "Tree", "Rock", "Mushroom", "Water",
            "PavedTile", "Axe", "Flamethrower", "Flash"
        })

        self._active_flashes = []  # flashes affect darkness only

        # initialize objects in grid
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], (r, c))
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        Grid.GRID_LIST[name] = self

    # * Simple Getters
    def get_player(self): return self.get_obj_in_coord(*self.__player_pos)

    def get_grid_obj_map(self): return self.__grid_obj_map

    def get_layers_from_coord(self, r, c): return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self): return self.__total_mushrooms

    def increment_total_mushrooms(self): self.__total_mushrooms += 1

    def get_dark_radius(self): return self._dark_radius

    def get_is_cleared(self): return self.__is_cleared

    @staticmethod
    def get_grid_by_name(name: str):
        if name not in Grid.GRID_LIST:
            raise KeyError(f"No grid found with name: {name}")
        return Grid.GRID_LIST[name]

    # * Complex Getters
    def pop_layer_from_coord(self, r: int, c: int, layer=-1): return self.get_grid_obj_map()[r][c].pop(layer)

    def get_obj_in_coord(self, r: int, c: int):
        from Classes.Entity import Entity
        def in_bounds(r, c): return 0 <= r < self.__map_rows and 0 <= c < self.__map_cols
        if not in_bounds(r, c):
            raise IndexError(f"coordinate {r,c} out of bounds")
        return self.__grid_obj_map[r][c][-1]

    def get_display_symbol_of_obj(self, obj, mode="emoji"):
        emoji_map = {
            self.ENTITIES["Player"]: "🧑",
            self.ENTITIES["Tree"]: "🌲",
            self.ENTITIES["Mushroom"]: "🍄",
            self.ENTITIES["Rock"]: "🪨 ",
            self.ENTITIES["Water"]: "🟦",
            self.ENTITIES["PavedTile"]: "⬜",
            self.ENTITIES["Axe"]: "🪓",
            self.ENTITIES["Flamethrower"]: "🔥",
            self.ENTITIES["Flash"]: "💡"
        }
        ascii_map = {
            self.ENTITIES["Player"]: "L",
            self.ENTITIES["Tree"]: "T",
            self.ENTITIES["Mushroom"]: "+",
            self.ENTITIES["Rock"]: "R",
            self.ENTITIES["Water"]: "~",
            self.ENTITIES["PavedTile"]: "_",
            self.ENTITIES["Axe"]: "x",
            self.ENTITIES["Flamethrower"]: "*",
            self.ENTITIES["Flash"]: "?"
        }
        char_map = emoji_map if mode == "emoji" else ascii_map
        for cm in char_map:
            if isinstance(obj, cm):
                return char_map[cm]

    # * Simple Setters
    def level_clear(self): self.__is_cleared = True
    def set_player_pos(self, pos: list[int]): self.__player_pos = pos

    # * Complex Setters
    def add_layer_to_coord(self, r, c, entity): self.get_grid_obj_map()[r][c].append(entity)

    # * Misc
    def init_coord(self, symbol, coord):
        if symbol in Grid.EMPTY_TILES:
            return None, "　"
        if symbol == "L": self.__player_pos = coord
        if symbol == "+": self.increment_total_mushrooms()

        character_map = {
            "L": (self.ENTITIES["Player"], "🧑"),
            "T": (self.ENTITIES["Tree"], "🌲"),
            "+": (self.ENTITIES["Mushroom"], "🍄"),
            "R": (self.ENTITIES["Rock"], "🪨 "),
            "~": (self.ENTITIES["Water"], "🟦"),
            "_": (self.ENTITIES["PavedTile"], "⬜"),
            "x": (self.ENTITIES["Axe"], "🪓"),
            "*": (self.ENTITIES["Flamethrower"], "🔥"),
            "?": (self.ENTITIES["Flash"], "💡")
        }
        item = character_map.get(symbol)
        if not item:
            raise ValueError(f"Unknown type symbol: {symbol}")
        item_type, display_val = item
        return item_type(coord, self, symbol), display_val

    # * Flash / Darkness
    def register_flash(self, flash):
        if flash not in self._active_flashes:
            self._active_flashes.append(flash)

    def _gather_active_flash_positions(self):
        flashes = []
        for fl in list(self._active_flashes):
            try:
                pos, radius = fl.get_pos(), fl.get_radius()
            except Exception:
                continue
            if pos is not None and radius > 0:
                flashes.append((pos, radius))
        return flashes

    def _compute_display_for_cell(self, r, c, obj, player_pos, dark_radius, flashes, mode):
        display = self.get_display_symbol_of_obj(obj, mode) if obj else "　"
        distance = abs(player_pos[0] - r) + abs(player_pos[1] - c)

        # lit by flash?
        if any(abs(fr[0][0] - r) + abs(fr[0][1] - c) <= fr[1] for fr in flashes):
            return display

        # darken if dark_radius is set and outside radius
        if dark_radius is not None and distance > dark_radius:
            display = "⬛" if mode == "emoji" else "#"

        return display

    def visualize_map(self, mode="emoji", dark_radius=None):
        dark_radius = self._dark_radius if dark_radius is None else dark_radius
        player_pos = self.__player_pos
        flashes = self._gather_active_flash_positions()
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj = self.get_obj_in_coord(r, c)
                self.__grid_user_display[r][c] = self._compute_display_for_cell(
                    r, c, obj, player_pos, dark_radius, flashes, mode
                )

    def update_all_flashes(self):
        for fl in list(self._active_flashes):
            fl.update_radius()
            if fl.get_radius() <= 0:
                self._active_flashes.remove(fl)

    # * Visualization Helpers
    def get_vis_map_as_str(self, mode="ascii"):
        self.visualize_map(mode)
        return "\n".join("".join(row) for row in self.__grid_user_display)

    def render(self, P, G, item_here, holding_anything, test_mode=False):
        self.update_all_flashes()
        total_mushrooms = G.get_total_mushrooms()
        mushrooms_collected = P.get_mushroom_count()
        win, lose = (mushrooms_collected == total_mushrooms), P.get_is_dead()

        self.visualize_map(dark_radius=G.get_dark_radius())

        os.system("cls" if os.name == "nt" else "clear")
        for row in self.__grid_user_display:
            print("".join(row))

        print(f"\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected")
        if win: print("You win!")
        if lose: print("You lose...")

        # additional options
        display_use_item = ''
        if P.get_item()!=None:
            if P.get_item().get_passive(): display_use_item = f"\n[F] Use passive item {P.get_item()}"

        if not win and not lose:
            terminal_gui = f"""
[W] Move up
[A] Move left
[S] Move down
[D] Move right
[Q] Quit level{display_use_item}
[!] Reset

{item_here}
{holding_anything or "Not holding anything"}

What will you do? 
"""
            print(terminal_gui, end="")

        return win or lose