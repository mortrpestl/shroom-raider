import os
from Classes.Entities.import_entities import import_entities


class Grid:
    """Grid (or Level) arranges Entities and keeps track of Entities' positions.

    Attributes:
        GRID_LIST: A dictionary that stores Grids by name.
        EMPTY_TILES: A set containing possible representations for empty tiles.
        name: A str representing the name of Grid.
        map_rows: An int that stores how many rows Grid has.
        map_cols: An int that stores how many columns Grid has.
        grid_vis_map: A list containing a representation of Grid usually from external text files.
        grid_obj_map: A list containing the Entities arranged by their position values.
        grid_user_display: A list containing the visual representation of Grid shown to the user.
    """
    #you can add more keys (e.g. 'L🧑' to 'L🧑F' to allow 'F' to move Player)
    
    GRID_LIST = dict()
    EMPTY_TILES = {'.'} #can add other looks for empty tiles for future use

    def __init__(self, name, map_data: str):
        """
        Converts map data to an instance of Grid (initializes Entities on Grid).

        Adds the new instance in GRID_LIST and connects adjacent trees for other functionality (namely, Flamethrower).

        Args:
            name: A str pertaining to the Grid's name.
            map_data: A str listing the Grid's construction.
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
        """Given a symbol and coordinates, create an instance of that Entity (if applicable)

        Args:
            symbol: A string pertaining to the ASCII representation of a given Entity
            coord: A list pertaining to the current coordinate
            entities: A list that contains child classes of Entity
            grid: A Grid instance that dictates where an Entity is
        
        Returns:
            A tuple of length 2 containing
            item_type: An Entity object (with appropriate type).
            item_display_value: The visual representation of this Entity. 

        Raises:
            ValueError: if symbol does not represent any Entity
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
        """Connects all adjacent trees in the Grid.

        Args:
            entities: A list that contains child classes of Entity.
        """
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                cell = self.get_obj_in_coord(r,c)
                Tree = entities["Tree"]
                if isinstance(cell, Tree): cell.find_neighbors(self.__grid_obj_map)
                
    @staticmethod
    def get_by_name(name):
        """ Gets Grid instance by name.

        Args:
            name: a Grid's name

        Returns:
            a Grid object

        Raises:
            KeyError: if there is no valid name in GRID_LIST
        """
        if name not in Grid.GRID_LIST:
            raise KeyError(f'No grid found with name:{name}')
        return Grid.GRID_LIST[name]

    def get_obj_in_coord(self, r: int, c: int):
        """Gets Entity at certain coordinates.

        Args:
            r: An int pertaining to the row coordinate
            c: An int pertaining to the column coordinate

        Returns:
            An Entity (or None) object in the given coordinates

        Raises:
            IndexError: if coordinates ([r,c]) are out of bounds
        """
        from Classes.Entity import Entity

        def in_bounds(r,c): return 0<=r<self.__map_rows and 0<=c<self.__map_cols

        if not in_bounds(r,c):
            raise IndexError(f'coordinate {r,c} out of bounds')
        
        return self.__grid_obj_map[r][c]

    def render(self):
        """Renders a given grid on the terminal"""
        
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
