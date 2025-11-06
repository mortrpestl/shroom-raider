from Classes.Entity import Entity

class Mushroom(Entity):

    # * Attributes
    _is_collectable = True

    def __init__(self, pos, on_grid, ascii='+'):
        super().__init__(pos, on_grid, ascii)

    # * Complex Setter
    def collect(self, p):
        p.increment_mushroom_count()
        self.destroy(-2)