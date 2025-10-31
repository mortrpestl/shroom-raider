from Classes.Entity import Entity

class PavedTile(Entity):

    # * Attributes
    _is_collectable = False
    _is_collideable = False

    def __init__(self, pos, on_grid, ascii='_'):
        super().__init__(pos, on_grid, ascii)