class Entity:
    __pos = []
    __icon = ""
    _is_collideable = False # If True, any other collideable object cannot occupy this Entity's space
    _is_collectable = False # If True, Player can collect this Entity
    _is_pushable = False # If True, Player can push this Entity
    _is_deadly = False # If True, Player gets game over'd when on it. 

    def __init__(self, pos: list, icon: str):
        self.__pos = pos
        self.__icon = icon

    def get_pos(self):
        return self.__pos
    
    def set_pos(self, direction: str):
        match direction:
            case "W": self.__pos[0] -= 1
            case "S": self.__pos[0] += 1
            case "A": self.__pos[1] -= 1
            case "D": self.__pos[1] += 1

    def get_icon(self):
        return self.__icon
    
    def set_icon(self, icon: str):
        self.__icon = icon

    def get_collideable(self):
        return self._is_collideable

    def get_collectable(self):
        return self._is_collectable

    def get_pushable(self):
        return self._is_pushable
    
    def get_deadly(self):
        return self._is_deadly
