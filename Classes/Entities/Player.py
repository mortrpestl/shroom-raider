from Classes.EntityTypes.Entity import Entity

import Flamethrower
import Axe

class Player(Entity):
    __item = None
    __mushroom_count = 0
    
    def __init__(self, pos: tuple, item: Entity): 
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


