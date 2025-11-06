from Classes.Entity import Entity

class PavedTile(Entity):
    def __init__(self, pos, on_grid, ascii='_'):
        super().__init__(pos, on_grid, ascii)