from Classes.Entity import Entity

class Mushroom(Entity):
    _is_collectable = True
    _is_collideable = False

    def __init__(self, pos, on_grid, ascii='+'):
        super().__init__(pos, on_grid, ascii)

    def collect(self, p):
        p.increment_mushroom_count()
        self.destroy()