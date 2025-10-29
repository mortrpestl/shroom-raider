from Classes.Entity import Entity

class Axe(Entity):
    
    # * Attributes
    _is_collectable = True
    _is_collideable = False

    def __init__(self, pos, on_grid, ascii='x'):
        super().__init__(pos, on_grid, ascii)