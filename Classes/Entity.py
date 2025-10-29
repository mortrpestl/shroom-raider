"""
TODO:
- Implement self._push() (checks inbounds, updates coordinates)
- Implement self.destroy() (destroys object from memory)
"""

from Classes.Entities.import_entities import import_entities

class Entity:
    """An Entity are objects placed inside a Level (Grid) with unique interactions and behaviors

    An Entity in a Grid is visually represented either by an emoji or by an ASCII representation.
    Furthermore, an Entity cannot exist without a Grid to reside in.
    

    Attributes:
        pos: A list of form, [row, column], within the Grid. [0, 0] is the top-left corner.
        on_grid: A Grid object where this Entity is residing in.
        is_collideable: A boolean indicating if this Entity has collision. 
            Specifically, no collideable Entity cannot have the same position as another collideable Entity
        is_collectable: A boolean indicating if this Entity can be collected (Generally, by Player)
        is_pushable: A boolean indicating if this Entity can be moved by another Entity
        is_deadly: A boolean indicating if this Entity causes a loss state upon interaction
    """

    _is_collideable = False # If True, any other collideable object cannot occupy this Entity's space
    _is_collectable = False # If True, Player can collect this Entity
    _is_pushable = False # If True, Player can push this Entity
    _is_deadly = False # If True, Player gets game over'd when on it. 
    _is_burnable = False # If True, triggers burning of Tree

    def __init__(self, pos: list, on_grid, ascii: str):
        """Initializes the instance based on position within the Grid its residing in
        Args:
            pos: Defines the position of this Entity.
            on_grid: Defines the Grid this Entity is residing in. 
        """
        from Classes.Grid import Grid #this placement is intentional, if outside, will hit circular import eerror
        self.__pos = pos
        self.__on_grid = on_grid
        self.__ascii = ascii
        
    def get_ascii(self):
        return self.__ascii
    
    def get_on_grid(self):
        return self.__on_grid
    
    def get_pos(self):
        """Get Entity's position
        
        Returns:
            A list containing two values, [r,c]: the row (r) and the column (c) its residing in
        """
        return self.__pos
    
    def push(self, direction, entity):
        """Push another Entity in the same direction this Entity moved

        Args:
            direction: The direction this Entity moved
            entity: The entity that will be pushed
        """
        # TODO check whether the pusher is a valid pusher (Rock cannot push Rock for ex.)
        return entity.set_pos(direction)

    def set_pos(self, directions, item=None):

        entities = import_entities({"Axe","Flamethrower"})


        """Move entity by one cell corresponding to directions in input
        
        Args:
            directions: String of instructions pertaining to movement
        Raises:
            Exception: This Entity collided with an unpushable, collideable Entity
        """

        free_to_move = False
        r,c = self.get_pos()
        on_grid = self.get_on_grid()
        pushed = True

        def in_bounds(r,c):
            return 0<=r<len(on_grid.get_grid_obj_map()) and 0<=c<len(on_grid.get_grid_obj_map()[0])
        
        for direction in directions:
            match direction.lower():
                case "w": r -= 1
                case "s": r += 1
                case "a": c -= 1
                case "d": c += 1
            if not in_bounds(r,c):
                return 
            target_obj = self.get_obj_in_coord(r, c)

            # TODO fix logic of this.
            if target_obj != None: 
                if target_obj.get_burnable():
                    if isinstance(item,entities["Flamethrower"]):
                        target_obj.burn_connected()
                        self.set_item(None)
                        free_to_move = True   
                    if isinstance(item,entities["Axe"]):
                        target_obj.chop()
                        self.set_item(None)
                        free_to_move = True                    

                if not free_to_move:
                    if target_obj.get_pushable(self):
                        pushed = self.push(direction, target_obj)
                    elif target_obj.get_collideable():
                        pushed = False
                        continue
            if pushed:
                on_grid.get_grid_obj_map()[self.__pos[0]][self.__pos[1]].pop()
                on_grid.get_grid_obj_map()[r][c].append(self)
                self.__pos = [r, c]
        else:
            return pushed
            
    

    def get_obj_in_coord(self, r, c):
        """Gets Entity on a coordinate residing in the same Grid

        Args:
            r: the row coordinate
            c: the column coordinate

        Returns:
            an Entity on the given coordinates
        """
        return self.__on_grid.get_obj_in_coord(r,c)

    def get_burnable(self):
        return self._is_burnable
    def get_collideable(self):
        """Gets this Entity's collision

        Returns:
            a boolean
        """
        return self._is_collideable

    def get_collectable(self):
        """Gets this Entity's collectability

        Returns:
            a boolean
        """

        return self._is_collectable

    def get_pushable(self, pusher):
        """Gets this Entity's pushability

        Returns:
            a boolean
        """
        try:
            return self._is_pushable
        except:
            return False
    
    def get_deadly(self):
        """Gets this Entity's deadliness.
        
        Returns:
            a boolean
        """
        return self._is_deadly  

    def destroy(self):
        """
        Destroys an object from the grid (and also deletes it)
        """
        r,c=self.get_pos()
        grid=self.get_on_grid()
        grid.get_grid_obj_map()[r][c].pop()