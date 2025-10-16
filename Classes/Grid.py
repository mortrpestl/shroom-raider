import os

from Classes.Entities import * 
from Classes.Entity import Entity

class Grid:
    #you can add more keys (e.g. 'L🧑' to 'L🧑F' to allow 'F' to move Player)
    TILE_MAP = [
        ('L🧑',Player),
        ('T🌲',Tree),
        ('+🍄',Mushroom), #implement
        ('R🪨',Stone), 
        ('~🟦',Water),
        ('-⬜',PavedTile)
        ] 
    
    
    #can add other looks for empty tiles for future use
    EMPTY_TILES = {'.'}

    tile_dict = {s:v for (pair,v) in TILE_MAP for s in list(pair)}
    grid_list = dict() #stores levels by level name

    def __init__(self, name, map_data: str):
        """
        Converts map data to list of strings, initializes objects on map
        """

        self.__name = name

        #convert string provided into grid
        self.__grid_vis_map = [list(rows) for rows in map_data.strip().split('\n')]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        self.__grid_obj_map = [[] for _ in range(self.__map_rows)]


        #initizalize all items and makes object map for collision detection
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj = Grid.init_coord(self.__grid_vis_map[r][c],(r,c))
                self.__grid_obj_map[r].append(obj)

        self.connect_trees()
        Grid.grid_list[name] = self

    @classmethod
    def init_coord(cls, symbol, coord):
        """
        Given a symbol and coordinates, create instance of that item (if applicable)
        """

        if symbol in Grid.EMPTY_TILES:
            return None 
        
        item_type = Grid.tile_dict.get(symbol)
        if not item_type:
            raise ValueError(f'Unknown type symbol: {symbol}')
        
        return item_type(coord)

    def connect_trees(self):
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                cell = self.get_obj_in_coord(r,c)
                if isinstance(cell,Tree): cell.find_neighbors(self.__grid_obj_map)
                
    @staticmethod
    def get_by_name(name):
        """
        Gets Grid instance by name.
        """
        if name not in Grid.grid_list:
            raise KeyError(f'No grid found with name:{name}')
        return Grid.grid_list[name]

    def get_obj_in_coord(self,r,c) -> Entity:
        """
        Gets item type at certain coordinate
        """
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

    