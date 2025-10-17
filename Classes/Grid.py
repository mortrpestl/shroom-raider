import os
from Classes.Entities.import_entities import import_entities


class Grid:
    #you can add more keys (e.g. 'L🧑' to 'L🧑F' to allow 'F' to move Player)
    
    GRID_LIST = dict() #stores levels by level name
    #can add other looks for empty tiles for future use
    EMPTY_TILES = {'.'}

    def __init__(self, name, map_data: str):
        """
        Converts map data to list of strings, initializes objects on map
        """

        self.__name = name

        #convert string provided into grid
        self.__grid_vis_map = [list(rows) for rows in map_data.strip().split('\n')]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        self.__grid_obj_map = [[] for _ in range(self.__map_rows)]
        self.__grid_user_display = [[] for _ in range(self.__map_rows)]

        entities = import_entities({"Player","Tree","Stone","Mushroom","Water","PavedTile","Axe","Flamethrower"})

        #initialize all items and makes object map for collision detection
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = Grid.init_coord(self.__grid_vis_map[r][c], (r,c), entities, self)
                self.__grid_obj_map[r].append(obj)
                self.__grid_user_display[r].append(display)

        self.connect_trees(entities)
        Grid.GRID_LIST[name] = self

    @classmethod
    def init_coord(cls, symbol, coord, entities, grid):
        """
        Given a symbol and coordinates, create instance of that item (if applicable)
        """
        if symbol in Grid.EMPTY_TILES:
            return None, "　"

        character_map = {
            'L': (entities["Player"], "🧑"),
            'T': (entities["Tree"], "🌲"),
            '+': (entities["Mushroom"], "🍄"),
            'R': (entities["Stone"], "🪨 "),
            '~': (entities["Water"], "🟦"),
            '-': (entities["PavedTile"], "⬜"),
            'x': (entities["Axe"], "🪓"),
            '*': (entities["Flamethrower"], "🔥")
        }

        item = character_map.get(symbol)

        if not item:
            raise ValueError(f'Unknown type symbol: {symbol}')
        
        item_type, item_display_value = item

        
        return item_type(coord, grid), item_display_value

    def connect_trees(self, entities):
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                cell = self.get_obj_in_coord(r,c)
                Tree = entities["Tree"]
                if isinstance(cell, Tree): cell.find_neighbors(self.__grid_obj_map)
                
    @staticmethod
    def get_by_name(name):
        """
        Gets Grid instance by name.
        """
        if name not in Grid.GRID_LIST:
            raise KeyError(f'No grid found with name:{name}')
        return Grid.GRID_LIST[name]

    def get_obj_in_coord(self,r,c):
        """
        Gets item type at certain coordinate
        """
        from Classes.Entity import Entity

        def in_bounds(r,c): return 0<=r<self.__map_rows and 0<=c<self.__map_cols

        if not in_bounds(r,c):
            raise IndexError(f'coordinate {r,c} out of bounds')
        
        return self.__grid_obj_map[r][c]

    def render(self):
        """
        Renders a given grid on the terminal
        """
        
        #clears system file
        os.system('cls' if os.name=='nt' else 'clear')
        """
        rudimentary display code
        """
        for i in self.__grid_vis_map:
            print(i)

        #for debugging
        for i in self.__grid_user_display:
            print(''.join(i))
