
"""
TODO:
- Implement self._push() (checks inbounds, updates coordinates)
- Implement self.destroy() (destroys object from memory)
"""


class Entity:

    def __init__(self, pos: list, on_grid):
        from Classes.Grid import Grid #this placement is intentional, if outside, will hit circular import eerror
        self.__pos = pos
        self.__on_grid = on_grid
        self._is_collideable = False # If True, any other collideable object cannot occupy this Entity's space
        self._is_collectable = False # If True, Player can collect this Entity
        self._is_pushable = False # If True, Player can push this Entity
        self._is_deadly = False # If True, Player gets game over'd when on it. 

    def get_pos(self):
        return self.__pos
    
    def push(self, direction, entity):
        # TODO check whether the pusher is a valid pusher (Rock cannot push Rock for ex.)
        entity.set_pos(direction)

    def set_pos(self, directions):
        # TODO (if necessary) add functionality to take in r, c as parameters (note: there is no method overloading in py)
        r, c = self.get_pos()
        for direction in directions:
            match direction.lower():
                case "w": r -= 1
                case "s": r += 1
                case "a": c -= 1
                case "d": c += 1
            target_obj = self.get_obj_in_coord(r, c)
            if target_obj.get_pushable(): 
                self.push(direction, target_obj)
            elif target_obj.get_collideable():
                raise Exception(f"collided with an unpushable entity!")
                #* probably wiser to implement a custom error for this
            self.__pos = [r,c]
    

    def get_obj_in_coord(self, r, c):
        return self.__on_grid.get_obj_in_coord(r,c)

        

    def get_collideable(self):
        return self._is_collideable

    def get_collectable(self):
        return self._is_collectable

    def get_pushable(self):
        return self._is_pushable
    
    def get_deadly(self):
        return self._is_deadly
