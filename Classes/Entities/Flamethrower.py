from Classes.Entity import Entity
from Classes.Entities.import_entities import import_entities


class Flamethrower(Entity):
    _is_collectable = True
    _is_collideable = False

    def __init__(self, pos, on_grid, ascii='*'):
        super().__init__(pos, on_grid, ascii)
