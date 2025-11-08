import os
from pygame import mixer as m
from Classes.Entity import Entity
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
        self.__dark_radius = dark_radius

        # convert string to grid
        self.__grid_vis_map = [list(row) for row in map_data.strip().split('\n')]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        self.__grid_obj_map = [[[None] for _ in range(self.__map_cols)] for _ in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

        self.ENTITIES = import_entities({
            "Player", "Tree", "Rock", "Mushroom", "Water",
            "PavedTile", "Axe", "Flamethrower", "Flash"
        })
        self.character_mapping = { # for display
                self.ENTITIES["Player"]: ("🧑", 'L'),
                self.ENTITIES["Tree"]: ("🌲", 'T'),
                self.ENTITIES["Mushroom"]: ("🍄", '+'),
                self.ENTITIES["Rock"]: ("🪨 ", 'R'),
                self.ENTITIES["Water"]: ("🟦", '~'),
                self.ENTITIES["PavedTile"]: ("⬜", '_'),
                self.ENTITIES["Axe"]: ("🪓", 'x'),
                self.ENTITIES["Flamethrower"]: ("🔥", '*'),
                self.ENTITIES["Flash"]: ("💡", "?")
        }
        self.initialization_map = {k[1]: (v, k[0]) for v, k in self.character_mapping.items()}

        self.__active_flashes = []  # flashes affect darkness only

        # initialize objects in grid
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], [r, c])
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        Grid.GRID_LIST[name] = self

    # * Simple Getters

    def get_player(self): return self.get_obj_in_coord(*self.__player_pos)

    def get_player_pos(self): return self.__player_pos

    def get_grid_obj_map(self): return self.__grid_obj_map

    def get_layers_from_coord(self, r: int, c: int): return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self): return self.__total_mushrooms

    def increment_total_mushrooms(self): self.__total_mushrooms += 1

    def get_dark_radius(self): return self.__dark_radius

    def get_is_cleared(self): return self.__is_cleared

    def get_active_flashes(self): return self.__active_flashes

    @staticmethod
    def get_grid_by_name(name: str):
        if name not in Grid.GRID_LIST:
            raise KeyError(f"No grid found with name: {name}")
        return Grid.GRID_LIST[name]

    # * Complex Getters
    def pop_layer_from_coord(self, r: int, c: int, layer: int =-1): return self.get_grid_obj_map()[r][c].pop(layer)

    def get_obj_in_coord(self, r: int, c: int, layer: int = -1):

        if not (0<=r<self.__map_rows and 0<=c<self.__map_cols):
            raise IndexError(f'coordinate {r,c} out of bounds')

        return self.__grid_obj_map[r][c][layer]

    def get_display_symbol_of_obj(self, obj: Entity | None, mode: str="emoji"):
        if mode=="emoji": offset = 0
        else: offset = 1
        
        for cm in self.character_mapping:
            if isinstance(obj, cm): return self.character_mapping[cm][offset]

    # * Simple Setters
    def level_clear(self): self.__is_cleared = True

    def set_player_pos(self, pos: list[int]): self.__player_pos = pos

    # * Complex Setters
    def add_layer_to_coord(self, r: int, c: int, entity: Entity): self.get_grid_obj_map()[r][c].append(entity)

    # * Misc
    def init_coord(self, symbol: str, coord: list):
        if symbol in Grid.EMPTY_TILES: return None, "　"
        if symbol == 'L': self.set_player_pos(coord)
        if symbol == '+': self.increment_total_mushrooms()

        item = self.initialization_map.get(symbol)

        if not item: raise ValueError(f'Unknown type symbol: {symbol}')
        
        item_type, item_display_value = item

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

    # * Visualization Helpers
    def __compute_display_for_cell(self, r: int, c: int, obj: Entity|None, mode: str):
        display = self.get_display_symbol_of_obj(obj, mode) if obj else "　"
        dark_radius = self.get_dark_radius()

        # skip darkness logic if no dark_radius
        if dark_radius == None: return display

        # * DARKNESS LOGIC
        # lit by flash? then display object
        if any(abs(fl.get_pos()[0] - r) + abs(fl.get_pos()[1] - c) <= fl.get_radius() 
               for fl in self.get_active_flashes()):
            return display

        # darken if dark_radius is set and outside radius
        distance = abs(self.get_player_pos()[0] - r) + abs(self.get_player_pos()[1] - c)
        if distance > dark_radius:
            display = "⬛" if mode == "emoji" else "#"

        return display

    def visualize_map(self, mode: str ="emoji"):
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj = self.get_obj_in_coord(r, c)
                self.__grid_user_display[r][c] = self.__compute_display_for_cell(
                    r, c, obj, mode
                )

    def get_vis_map_as_str(self, mode: str ="ascii"):
        self.visualize_map(mode)
        return "\n".join("".join(row) for row in self.__grid_user_display)

    def render(self, p: Entity, test_mode: bool =False):
        self.update_all_flashes()
        total_mushrooms = self.get_total_mushrooms()
        mushrooms_collected = p.get_mushroom_count()
        item_here = p.get_entity_below().__class__.__name__ #element below player
        held_item = p.get_item().__class__.__name__
        
        win, lose = (mushrooms_collected == total_mushrooms), p.get_is_dead()

        self.visualize_map()

        os.system("cls" if os.name == "nt" else "clear")
        for row in self.__grid_user_display:
            print("".join(row))

        print(f"\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected")
        if win: print("You win!")
        if lose: print("You lose...")

        # additional options
        display_use_item = ''
        if p.get_item()!=None:
            if p.get_item().get_passive(): display_use_item = f"\n[F] Use passive item {p.get_item()}"

        if not win and not lose:
            terminal_gui = f"""
[W] Move up
[A] Move left
[S] Move down
[D] Move right
[Q] Quit level{display_use_item}
[!] Reset

{item_here + ' is here' if item_here != 'NoneType' else 'Nothing Here'}
{f'Holding item {held_item}' if held_item != "NoneType" else "Not holding anything"}

What will you do? """
            print(terminal_gui, end="")

        return win or lose