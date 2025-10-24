from Classes.Entity import Entity

class Stone(Entity):
    def get_pushable(self, pusher):
        if isinstance(pusher, Stone):
            return False
        return True