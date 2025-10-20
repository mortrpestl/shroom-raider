from Classes.Entity import Entity

class Water(Entity):
    _is_collectable = False
    _is_collideable = False
    _is_deadly = True

    def __init__(self, pos, on_grid, ascii='~'):
        super().__init__(pos, on_grid, ascii)