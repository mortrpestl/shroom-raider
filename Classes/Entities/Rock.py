from Classes.Entity import Entity
from Classes.Entities.import_entities import import_entities

class Rock(Entity):

    # * Attributes
    _is_collectable = False
    _is_collideable = True
    _is_pushable = True
    

    def __init__(self, pos, on_grid, ascii='R'):
        super().__init__(pos, on_grid, ascii)

    # * Complex Getters

    def get_movement_validity(self, direction, r, c):
        target_obj = self.get_obj_in_coord(r, c)

        if target_obj == None: return True
        
        if target_obj.get_collectable():
            return False # cannot move on collectables.
        
        return super().get_movement_validity(direction, r, c)
    
    def get_pushable(self, pusher):
        entities = import_entities({"Player"})
        if isinstance(pusher, entities["Player"]):
            return True
        else:
            return False
    
    # * Simple Setters
    def set_pos(self, directions): return super().set_pos(directions)


    
        
    

