import os
from Classes.Entities.import_entities import import_entities

class Grid:
    
    # * Attributes
    GRID_LIST = dict()
    EMPTY_TILES = '.' #can add other looks for empty tiles for future use

    def __init__(self, name, map_data: str):

        self.__name = name
        self.__player_pos = [0, 0]
        self.__total_mushrooms = 0
        self.__is_cleared = False

        #convert string provided into grid
        self.__grid_vis_map = [list(rows) for rows in map_data.strip().split('\n')]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        self.__grid_obj_map = [[[None] for c in range(self.__map_cols)] for r in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

        self.ENTITIES = import_entities({"Player","Tree","Rock","Mushroom","Water","PavedTile","Axe","Flamethrower"})

        #initialize all items and makes object map for collision detection
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], (r,c))
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        Grid.GRID_LIST[name] = self
    
    # * Simple Getters

    def get_player(self): return self.get_obj_in_coord(*self.__player_pos)

    def get_grid_obj_map(self): return self.__grid_obj_map
    
    def get_layers_from_coord(self,r,c): return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self): return self.__total_mushrooms

    def increment_total_mushrooms(self): self.__total_mushrooms += 1
    # * Complex Getters

    def pop_layer_from_coord(self,r,c,layer=-1): return self.get_grid_obj_map()[r][c].pop(layer)

    def get_is_cleared(self): return self.__is_cleared

    @staticmethod
    def get_grid_by_name(name):

        if name not in Grid.GRID_LIST:
            raise KeyError(f'No grid found with name:{name}')
        return Grid.GRID_LIST[name]
    
    def get_obj_in_coord(self, r: int, c: int):

        from Classes.Entity import Entity

        def in_bounds(r,c): return 0<=r<self.__map_rows and 0<=c<self.__map_cols

        if not in_bounds(r,c):
            raise IndexError(f'coordinate {r,c} out of bounds')
        
        return self.__grid_obj_map[r][c][-1]
    
    def get_display_symbol_of_obj(self, obj, mode="emoji"):
        if mode=="emoji":
            character_map = {
                self.ENTITIES["Player"]: "🧑",
                self.ENTITIES["Tree"]: "🌲",
                self.ENTITIES["Mushroom"]: "🍄",
                self.ENTITIES["Rock"]: "🪨 ",
                self.ENTITIES["Water"]: "🟦",
                self.ENTITIES["PavedTile"]: "⬜",
                self.ENTITIES["Axe"]: "🪓",
                self.ENTITIES["Flamethrower"]: "🔥"
            }
        else:
            character_map = {
                self.ENTITIES["Player"]: "L",
                self.ENTITIES["Tree"]: "T",
                self.ENTITIES["Mushroom"]: "+",
                self.ENTITIES["Rock"]: "R",
                self.ENTITIES["Water"]: "~",
                self.ENTITIES["PavedTile"]: "_",
                self.ENTITIES["Axe"]: "x",
                self.ENTITIES["Flamethrower"]: "*"
            }

        for cm in character_map:
            if isinstance(obj, cm): return character_map[cm]

    # * Simple Setters

    def level_clear(self): #clear/win the level
        self.__is_cleared = True

    # * Complex Setters

    def add_layer_to_coord(self,r,c,entity):
        self.get_grid_obj_map()[r][c].append(entity)
    
    # * Misc 

    def init_coord(self, symbol, coord):

        if symbol in Grid.EMPTY_TILES:
            return None, "　"
        
        if symbol == 'L':
            self.__player_pos = coord

        if symbol == '+':
            self.increment_total_mushrooms()

        character_map = {
            'L': (self.ENTITIES["Player"], "🧑"),
            'T': (self.ENTITIES["Tree"], "🌲"),
            '+': (self.ENTITIES["Mushroom"], "🍄"),
            'R': (self.ENTITIES["Rock"], "🪨 "),
            '~': (self.ENTITIES["Water"], "🟦"),
            '_': (self.ENTITIES["PavedTile"], "⬜"),
            'x': (self.ENTITIES["Axe"], "🪓"),
            '*': (self.ENTITIES["Flamethrower"], "🔥")
        }

        item = character_map.get(symbol)

        if not item:
            raise ValueError(f'Unknown type symbol: {symbol}')
        
        item_type, item_display_value = item

        return item_type(coord, self, symbol), item_display_value
    
    def visualize_map(self, mode='emoji'):
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj_in_coord = self.get_obj_in_coord(r,c)
                
                if not obj_in_coord: 
                    self.__grid_user_display[r][c] = "　" if mode=='emoji' else "."
                else:
                    self.__grid_user_display[r][c] = self.get_display_symbol_of_obj(obj_in_coord, mode)

    def get_vis_map_as_str(self,mode='ascii'):
        grid_str_rep = []

        self.visualize_map(mode)

        for row in self.__grid_user_display:
            grid_str_rep.append(''.join(row))

        return '\n'.join(grid_str_rep)
    
    def render(self, P, G, item_here, holding_anything, test_mode=False):
        total_mushrooms = G.get_total_mushrooms()
        mushrooms_collected = P.get_mushroom_count()

        win = (mushrooms_collected == total_mushrooms)
        lose = P.get_is_dead()

        self.visualize_map()

        os.system('cls' if os.name=='nt' else 'clear')

        for row in self.__grid_user_display:
            print(''.join(row))

        print(f'\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected')

        if win:
            print('You win!')
        if lose:
            print('You lose...')

        if not win and not lose:
            terminal_gui = f"""\n[W] Move up\n[A] Move left\n[S] Move down\n[D] Move right\n[!] Reset\n\n{item_here}\n{holding_anything if holding_anything is not None else "Not holding anything"}\n\nWhat will you do? """
            print(terminal_gui,end='')

        if win or lose:
            return True
        return False
