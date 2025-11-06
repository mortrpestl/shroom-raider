from Classes.Entities.import_entities import import_entities

class Entity:

    # * Attributes
    _is_collideable = False # If True, any other collideable object cannot occupy this Entity's space
    _is_collectable = False # If True, Player can collect this Entity
    _is_pushable = False # If True, Player can push this Entity
    _is_deadly = False # If True, Player gets game over'd when on it. 
    _is_burnable = False # If True, triggers burning of Tree
    _is_passive = False # If True, affects the map in some way without having to be directly used on another object

    def __init__(self, pos: list, on_grid, ascii: str):
        from Classes.Grid import Grid #this placement is intentional, if outside, will hit circular import eerror
        self.__pos = list(pos)
        self.__on_grid = on_grid
        self.__ascii = ascii

    # * Simple Getters
        
    def __repr__(self): return self.__class__.__name__

    def get_ascii(self): return self.__ascii
    
    def get_on_grid(self): return self.__on_grid
    
    def get_pos(self): return self.__pos

    def get_obj_in_coord(self, r, c): return self.__on_grid.get_obj_in_coord(r,c)

    def get_burnable(self): return self._is_burnable

    def get_collideable(self): return self._is_collideable

    def get_collectable(self): return self._is_collectable

    def get_deadly(self): return self._is_deadly

    def get_passive(self): return self._is_passive
    
    # * Complex Getters

    def get_pushable(self, pusher): # TODO complete, or refactor
        try:
            return self._is_pushable
        except:
            return False

    def get_movement_validity(self, direction, r, c):
        on_grid = self.get_on_grid() # always get grid first
        rows = len(on_grid.get_grid_obj_map())
        cols = len(on_grid.get_grid_obj_map()[0])

        # Is the target coordinate out of the Grid? then you cannot move. 
        if not ((0<=r<rows) and (0<=c<cols)):
            return False
        
        # now, get the object if in bounds
        target_obj = self.get_obj_in_coord(r, c)
        
        # Is there nothing? then you are free to move
        if target_obj == None: return True
        
        # Is the object pushable? then TRY to push that object.
        if target_obj.get_pushable(self):
            return target_obj.set_pos(direction) # If the target entity cannot move, then the current entity cannot too.
            
        # Is the object collideable, otherwise? then you cannot move to that.
        elif target_obj.get_collideable():
            return False

        return True

    # * Simple Setters
    def set_coordinate(self, r, c):
        self.__pos = [r, c]

    # * Complex Setters

    def set_pos(self, directions):
        r,c = self.get_pos()
        on_grid = self.get_on_grid()

        for direction in directions:
            match direction.lower():
                case "w": r -= 1
                case "s": r += 1
                case "a": c -= 1
                case "d": c += 1

            if self.get_movement_validity(direction, r, c):
                on_grid.pop_layer_from_coord(*self.__pos)
                on_grid.add_layer_to_coord(r, c, self)
                self.set_coordinate(r, c)
            else:
                return False # The Entity failed to move (important for push logic)
        return True # The Entity has moved

    def destroy(self,layer=-1):
        self.get_on_grid().pop_layer_from_coord(*self.get_pos(), layer)

    # * Misc functions