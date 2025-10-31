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
                entities = import_entities({"Water", "PavedTile"})
                if isinstance(on_grid.get_obj_in_coord(r, c), entities["Water"]):
                    new_paved_tile = entities["PavedTile"]((r, c), self.get_on_grid(), '-') #make new paved tile
                    on_grid.pop_layer_from_coord(r, c).destroy() # remove the water
                    on_grid.add_layer_to_coord(r, c, new_paved_tile) # add the paved tile
                    self.destroy() # destroy self
                else:
                    on_grid.pop_layer_from_coord(*self.get_pos())
                    on_grid.add_layer_to_coord(r, c, self)
                    self.set_coordinate(r, c)
            else:
                return False # The Entity failed to move (important for push logic)
        return True # The Entity has moved


    
        
    

