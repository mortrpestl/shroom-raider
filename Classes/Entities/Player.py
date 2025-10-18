from Classes.Entity import Entity
from Classes.Grid import Grid
from Classes.Entities.import_entities import import_entities


needed = {"Flamethrower", "Axe"}
items = import_entities(needed)
Flamethrower = items["Flamethrower"]
Axe = items["Axe"]

class Player(Entity):
    """Inherits Entity. Player acts as the user's representation in the game. 

    Attributes:
        See Base class.
        item: an Entity (or None) that the Player is currently holding
        mushroom_count: the number of mushrooms that the Player has collected
    """
    def __init__(self, pos: list, on_grid: Grid, item: Entity | None = None):
        """Initializes a Player (Entity) with additional item param.

        Args:
            See Base class.
            item: the item the Player is currently holding
        """
        super().__init__(pos, on_grid)
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


