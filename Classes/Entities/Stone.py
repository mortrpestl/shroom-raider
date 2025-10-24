from Classes.Entity import Entity

class Stone(Entity):
    _is_collectable = False
    _is_collideable = True
    _is_pushable = True

    def __init__(self, pos, on_grid, ascii='R'):
        super().__init__(pos, on_grid, ascii)
