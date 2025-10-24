from Classes.Entity import Entity
from Classes.Grid import Grid
from Classes.Entities.import_entities import import_entities


needed = {"Flamethrower", "Axe", "Mushroom"}
items = import_entities(needed)
Flamethrower = items["Flamethrower"]
Axe = items["Axe"]
Mushroom = items["Mushroom"]

inventory = set()

class Player(Entity):
    """Inherits Entity. Player acts as the user's representation in the game. 

    Attributes:
        See Base class.
        item: an Entity (or None) that the Player is currently holding
        mushroom_count: the number of mushrooms that the Player has collected
    """
    def __init__(self, pos: list, on_grid: Grid, ascii = 'L',item: Entity | None = None):
        """Initializes a Player (Entity) with additional item param.

        Args:
            See Base class.
            item: the item the Player is currently holding
        """
        super().__init__(pos, on_grid, ascii)
        self.__item = item
        self.__mushroom_count = 0

    # ! code below was generated using AI 
    # ! prompt: make me the getters and setters for the attributes of this class

    def get_item(self):
        """Gets current item Player is holding
        
        Returns:
            a boolean.
        """
        return self.__item

    def set_item(self, item: Entity):
        """Sets current item to a different item

        Args:
            item: an Entity
        """
        self.__item = item
    
    def use_item(self):
        """Uses item; thereby, setting it to None"""
        self.__item = None

    def get_mushroom_count(self):
        """Gets current mushrooms Player has collected
        
        Returns:
            a boolean.
        """
        return self.__mushroom_count

    def increment_mushroom_count(self):
        """Increases mushroom count by 1"""
        self.__mushroom_count += 1

    def above_item(self):
        r,c = self.get_pos()
        on_grid = self.get_on_grid()

        stack = on_grid.get_layers_from_coord(r,c)
        player = stack[-1] if stack else None
        item = stack[-2] if len(stack) > 1 else None

        is_item = isinstance(item, (Axe, Flamethrower))

        if is_item: return item.__class__.__name__
        return False

    def above_mushroom(self):
        r,c = self.get_pos()
        on_grid = self.get_on_grid()

        stack = on_grid.get_layers_from_coord(r,c)
        player = stack[-1] if stack else None
        shroom = stack[-2] if len(stack) > 1 else None

        is_item = isinstance(shroom, Mushroom)

        if is_item: return shroom
        return False
    
    def collect_item(self):
        r,c = self.get_pos()
        on_grid = self.get_on_grid()

        #this option should only be SHOWN if there is an item, thus a method "item_below()" is recommended to be implemented (note: i did above with a different name)
        player = on_grid.pop_layer_from_coord(r,c)
        item = on_grid.pop_layer_from_coord(r,c)

        if isinstance(item,(Axe,Flamethrower)):
            self.set_item(item)
        elif item is not None:
            on_grid.add_layer_to_coord(r,c,item)

        on_grid.add_layer_to_coord(r,c,player)


