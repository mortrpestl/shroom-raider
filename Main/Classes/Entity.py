class Entity:
    """The superclass for all entities that exist in the game

    Some functions in this class are overwritten by some of the child classes

    Attributes:
        _is_collideable: If True, any other collideable object cannot occupy this Entity's space
        _is_collectable: If True, Player can collect this Entity
        _is_storable: If True, then Player can keep this in inventory
        _is_pushable: If True, Player can push this Entity
        _is_deadly: If True, Player gets game over'd when on it.
        _is_burnable: If True, triggers burning of Tree

        __pos: [r, c], the row and column of the Grid where the entity is located
        __on_grid: The Grid object that contains the entity
        __ascii: The ascii symbol that represents the entity
    """
    _is_collideable = False
    _is_collectable = False  
    _is_storable = False 
    _is_pushable = False 
    _is_deadly = False  
    _is_burnable = False  

    def __init__(self, pos: list, on_grid, ascii: str):
        """Initializes an Entity object

        Args: 
            pos: [r, c], the row and column of the entity on the given Grid
            on_grid: The grid which contains this entity
            ascii: The ascii character which corresponds to this entity
        """
        self.__pos = list(pos)
        self.__on_grid = on_grid
        self.__ascii = ascii

    # * Simple Getters

    def get_ascii(self):
        """
        Returns: The ascii character representation of the Entity
        """
        return self.__ascii

    def get_on_grid(self):
        """
        Returns: The Grid object that this Entity resides in
        """
        return self.__on_grid

    def get_pos(self):
        """
        Returns: The position [r, c] of this Entity in its Grid
        """
        return self.__pos

    def get_obj_in_coord(self, r: int, c: int):
        """
        Returns: The object on coordinate [r, c] on the same Grid as this Entity
        """
        return self.__on_grid.get_obj_in_coord(r, c)


    """
    The following functions contain the simple getters for all the basic class attributes
    """
    def get_burnable(self):
        """
        Returns: A boolean indicating if an object is burnable or not
        """
        return self._is_burnable

    def get_collideable(self):
        """
        Returns: A boolean indicating if an object is collideable or not
        """
        return self._is_collideable or self._is_pushable

    def get_collectable(self):
        """
        Returns: A boolean indicating if an object is collectible or not
        """
        return self._is_collectable or self._is_storable
          

    def get_storable(self):
        """
        Returns: A boolean indicating if an object is storable or not
        """
        return self._is_storable

    def get_deadly(self):
        """
        Returns: A boolean indicating if an object is deadly or not
        """
        return self._is_deadly

    def get_pushable(self):
        """
        Returns: A boolean indicating if an object is pushable or not
        """
        return self._is_pushable

    # * Complex Getters


    def in_bounds(self, r: int, c: int):
        """Checks if the Entity is within the bounds of its Grid

        Args: 
            r, c: The row and column position of the Entity

        Returns:
            A boolean indicating if the Entity is within the bounds of its Grid
        """
        on_grid = self.get_on_grid()
        rows = len(on_grid.get_grid_obj_map())
        cols = len(on_grid.get_grid_obj_map()[0])

        if (0 <= r < rows) and (0 <= c < cols):
            return True
        else:
            return False

    def get_movement_validity(self, direction: str, r: int, c: int):
        """Checks if an Entity can move in a certain direction

        Args:
            direction: "wasd", where the Entity intends to move
            r, c: The current row and column position of the Entity

        Returns: 
            A bool indicating if the Entity can move
        """
        if not self.in_bounds(r, c):
            return False

        # get the object
        target_obj = self.get_obj_in_coord(r, c)

        # Is there nothing? then you are free to move
        if target_obj is None:
            return True

        # Is the object pushable? then TRY to push that object.
        if target_obj.get_pushable(self):
            return target_obj.set_pos(
                direction
            )  # If the target entity cannot move, then the current entity cannot too.

        # Is the object collideable, otherwise? then you cannot move to that.
        elif target_obj.get_collideable():
            return False

        return True

    def get_entity_below(self):
        """ 
        Returns: The Entity that exists below this Entity in the Grid
        """
        stack = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        return stack[-2] if len(stack) > 1 else None

    # * Simple Setters
    def set_coordinate(self, r: int, c: int):
        """
        Sets the position of this Entity. DOES NOT MODIFY THE GRID
        """
        self.__pos = [r, c]

    # * Complex Setters

    def set_pos(self, direction: str):
        """Moves the Entity on the Grid

        Args: 
            direction: The direction that the Entity wants to move

        Returns:
            A boolean indicating if the move was successful
        """
        r, c = self.get_pos()
        on_grid = self.get_on_grid()

        match direction.lower():
            case "w":
                r -= 1
            case "s":
                r += 1
            case "a":
                c -= 1
            case "d":
                c += 1

        if self.get_movement_validity(direction, r, c):
            on_grid.pop_layer_from_coord(*self.__pos)
            on_grid.add_layer_to_coord(r, c, self)
            self.set_coordinate(r, c)
        else:
            return False  # The Entity failed to move (important for push logic)
        return True  # The Entity has moved

    def destroy(self):
        """
        Destroys the Entity, and removes it from the Grid
        """
        on_grid_stck = self.get_on_grid().get_layers_from_coord(*self.get_pos())
        for i in range(-1, -len(on_grid_stck) - 1, -1):
            if on_grid_stck[i] == self:
                self.get_on_grid().pop_layer_from_coord(*self.get_pos(), i)
                break

    # * Misc functions
