import os
from Classes.Entities.import_entities import import_entities

class Grid:
    
    # * Attributes
    GRID_LIST = dict()
    EMPTY_TILES = '.' #can add other looks for empty tiles for future use

    def __init__(self, name, map_data: str):

        self.__name = name
        self.__player_pos = (0, 0)

        #convert string provided into grid
        self.__grid_vis_map = [list(rows) for rows in map_data.strip().split('\n')]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        self.__grid_obj_map = [[[None] for c in range(self.__map_cols)] for r in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

        entities = import_entities({"Player","Tree","Rock","Mushroom","Water","PavedTile","Axe","Flamethrower"})

        #initialize all items and makes object map for collision detection
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], (r,c), entities)
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        # self.connect_trees(entities) #! refactor, we will be connecting trees on the fly now
        Grid.GRID_LIST[name] = self
    
    # * Simple Getters

    def get_player(self): return self.get_obj_in_coord(*self.__player_pos)

    def get_grid_obj_map(self): return self.__grid_obj_map
    
    def get_layers_from_coord(self,r,c): return self.__grid_obj_map[r][c]

    # * Complex Getters

    def pop_layer_from_coord(self,r,c): return self.get_grid_obj_map()[r][c].pop()

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
    
    def get_display_symbol_of_obj(self, obj):
        entities = import_entities({"Player","Tree","Rock","Mushroom","Water","PavedTile","Axe","Flamethrower"})

        character_map = {
            entities["Player"]: "🧑",
            entities["Tree"]: "🌲",
            entities["Mushroom"]: "🍄",
            entities["Rock"]: "🪨 ",
            entities["Water"]: "🟦",
            entities["PavedTile"]: "⬜",
            entities["Axe"]: "🪓",
            entities["Flamethrower"]: "🔥"
        }

        for cm in character_map:
            if isinstance(obj, cm): return character_map[cm]

    # * Simple Setters

    # * Complex Setters

    def add_layer_to_coord(self,r,c,entity):
        self.get_grid_obj_map()[r][c].append(entity)
    
    # * Misc 

    def init_coord(self, symbol, coord, entities):

        if symbol in Grid.EMPTY_TILES:
            return None, "　"
        
        if symbol == 'L':
            self.__player_pos = coord

        character_map = {
            'L': (entities["Player"], "🧑"),
            'T': (entities["Tree"], "🌲"),
            '+': (entities["Mushroom"], "🍄"),
            'R': (entities["Rock"], "🪨 "),
            '~': (entities["Water"], "🟦"),
            '-': (entities["PavedTile"], "⬜"),
            'x': (entities["Axe"], "🪓"),
            '*': (entities["Flamethrower"], "🔥")
        }

        item = character_map.get(symbol)

        if not item:
            raise ValueError(f'Unknown type symbol: {symbol}')
        
        item_type, item_display_value = item

        return item_type(coord, self, symbol), item_display_value
    
    def visualize_map(self):

        # ! refactor later
        entities = import_entities({"Player","Tree","Rock","Mushroom","Water","PavedTile","Axe","Flamethrower"})
        

        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj_in_coord = self.get_obj_in_coord(r,c)
                
                if not obj_in_coord: 
                    self.__grid_user_display[r][c] = "　"
                else:
                    self.__grid_user_display[r][c] = self.get_display_symbol_of_obj(obj_in_coord)

    def render(self):
        
        self.visualize_map()
        #clears system file
        os.system('cls' if os.name=='nt' else 'clear')

        for i in self.__grid_user_display:
            print(''.join(i))
