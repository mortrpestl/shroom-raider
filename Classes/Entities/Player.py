from Classes.Entity import Entity
from Classes.Entities.import_entities import import_entities

needed = {"Flamethrower", "Axe"}
items = import_entities(needed)
Flamethrower = items["Flamethrower"]
Axe = items["Axe"]

class Player(Entity):
    __item = None
    __mushroom_count = 0
    
    def __init__(self, pos: tuple, item: Entity = None): 
        self.__pos = pos
        self.__item = item
        self.__mushroom_count = 0

    # ! code below was generated using AI 
    # ! prompt: make me the getters and setters for the attributes of this class
    def get_item(self):
        return self.__item

    def set_item(self, item: Entity):
        self.__item = item
    
    def use_item(self):
        self.__item = None

    def get_mushroom_count(self):
        return self.__mushroom_count

    def increment_mushroom_count(self):
        self.__mushroom_count += 1


