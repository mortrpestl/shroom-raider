from typing import ClassVar

from classes.entities.import_entities import import_entities
from classes.entity import Entity
from utils.enums import ExitCodes


class Grid:
    """Represent the play area where players and all game objects reside.

    The Grid is a 3D data structure: a 2D list where each coordinate contains a stack of entities.
    """

    # Class-level dictionary of all grids
    GRID_LIST: ClassVar[dict[str, "Grid"]] = {}

    def __init__(self, name: str, map_data: str) -> None:
        """Initialize a Grid object from a stage string.

        Args:
            name (str): The name of the Grid
            map_data (str): A string representation of the stage

        """
        self.__name: str = name
        self.__player_pos: list[int] = [0, 0]
        self.__total_mushrooms: int = 0
        self.__is_cleared: bool = False

        self.__grid_vis_map: list[list[str]] = [list(row) for row in map_data.strip().split("\n")]
        self.__map_rows, self.__map_cols = len(self.__grid_vis_map), len(self.__grid_vis_map[0])
        # split long line to fix E501
        self.__grid_obj_map: list[list[list[Entity | None]]] = [
            [[None] for _ in range(self.__map_cols)] for _ in range(self.__map_rows)
        ]
        self.__grid_user_display: list[list[str]] = [[] for _ in range(self.__map_rows)]

        self.ENTITIES: dict[str, type[Entity]] = import_entities({
            "Player",
            "Tree",
            "Rock",
            "Mushroom",
            "Water",
            "PavedTile",
            "Axe",
            "Flamethrower",
        })

        # Display mappings
        self.character_mapping: dict[type[Entity], tuple[str, str]] = {
            self.ENTITIES["Player"]: ("🧑", "L"),
            self.ENTITIES["Tree"]: ("🌲", "T"),
            self.ENTITIES["Mushroom"]: ("🍄", "+"),
            self.ENTITIES["Rock"]: ("🪨", "R"),
            self.ENTITIES["Water"]: ("🟦", "~"),
            self.ENTITIES["PavedTile"]: ("⬜", "_"),
            self.ENTITIES["Axe"]: ("🪓", "x"),
            self.ENTITIES["Flamethrower"]: ("🔥", "*"),
        }
        self.initialization_map: dict[str, tuple[type[Entity], str]] = {
            k[1]: (v, k[0]) for v, k in self.character_mapping.items()
        }

        # Initialize objects in grid
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj, display = self.init_coord(self.__grid_vis_map[r][c], [r, c])
                self.__grid_obj_map[r][c].append(obj)
                self.__grid_user_display[r].append(display)

        Grid.GRID_LIST[self.__name] = self

    # * Simple Getters

    def get_player(self) -> Entity | None:
        """Return the Player entity on the Grid.

        Returns:
            The Player entity if present, otherwise None.

        """
        return self.get_obj_in_coord(*self.__player_pos)

    def get_grid_obj_map(self) -> list[list[list[Entity | None]]]:
        """Return the 2D list of entity stacks on the Grid.

        Returns:
            The internal 2D list of stacks representing entities.

        """
        return self.__grid_obj_map

    def get_layers_from_coord(self, r: int, c: int) -> list[Entity | None]:
        """Return the stack of entities at coordinate (r, c).

        Args:
            r (int): Row index.
            c (int): Column index.

        Returns:
            A list representing the stack of entities at (r, c).

        """
        return self.__grid_obj_map[r][c]

    def get_total_mushrooms(self) -> int:
        """Return the total number of mushrooms in the Grid.

        Returns:
            The integer count of mushrooms in this grid.

        """
        return self.__total_mushrooms

    def get_is_cleared(self) -> bool:
        """Return True if the Grid has been cleared.

        Returns:
            True if the grid is cleared, else False.

        """
        return self.__is_cleared

    # * Complex Getters

    def pop_layer_from_coord(self, r: int, c: int, layer: int = -1) -> Entity | None:
        """Remove and return an entity at a specific coordinate and layer.

        Args:
            r (int): Row index.
            c (int): Column index.
            layer (int): Layer index.

        Returns:
            The popped entity, or None if that layer held None.

        """
        return self.get_grid_obj_map()[r][c].pop(layer)

    @staticmethod
    def get_grid_by_name(name: str) -> "Grid":
        """Return a Grid object by its name.

        Args:
            name (str): name of the Grid

        Returns:
            The Grid instance with the given name.

        Raises:
            KeyError: If no Grid with the given name exists.

        """
        if name not in Grid.GRID_LIST:
            raise KeyError(f"No grid found with name:{name}")
        return Grid.GRID_LIST[name]

    def get_obj_in_coord(self, r: int, c: int, layer: int = -1) -> Entity | None:
        """Return the entity at coordinate (r, c) and layer, or None.

        Args:
            r (int): Row index.
            c (int): Column index.
            layer (int): Layer index.

        Returns:
            The entity located at (r, c, layer) or None.

        Raises:
            IndexError: If the coordinate is out of Grid bounds.

        """
        if not (0 <= r < self.__map_rows and 0 <= c < self.__map_cols):
            raise IndexError(f"Coordinate {r, c} out of bounds")
        return self.__grid_obj_map[r][c][layer]

    def get_display_symbol_of_obj(self, obj: Entity | None, mode: str = "emoji") -> str | None:
        """Return the visual representation of an object.

        Args:
            obj (Entity | None): The object being checked
            mode (str): The display mode

        Returns:
            A string representing the display symbol, or None if no mapping.

        """
        offset = 0 if mode == "emoji" else 1
        for cm in self.character_mapping:
            if isinstance(obj, cm):
                return self.character_mapping[cm][offset]
        return None

    # * Simple Setters

    def level_clear(self) -> None:
        """Mark the level as cleared."""
        self.__is_cleared = True

    def increment_total_mushrooms(self) -> None:
        """Increment the total mushroom count."""
        self.__total_mushrooms += 1

    # * Complex Setters

    def add_layer_to_coord(self, r: int, c: int, obj: Entity | None) -> None:
        """Add an entity to a specific coordinate.

        Args:
            r (int): Row index.
            c (int): Column index.
            obj (Entity | None): The object to be added into the Grid

        """
        self.get_grid_obj_map()[r][c].append(obj)

    # * Misc

    def init_coord(self, symbol: str, coord: list[int]) -> tuple[Entity | None, str]:
        """Return the entity and display character for a given symbol.

        Args:
            symbol (str): The character at the given coordinate
            coord (list): [r, c], The current coordinate being initialized

        Returns:
            A tuple of (entity instance or None, display character for that tile).

        Raises:
            ValueError: If the symbol is invalid.

        """
        if symbol == ".":
            return None, "　"
        if symbol == "L":
            self.__player_pos = coord
        if symbol == "+":
            self.increment_total_mushrooms()

        item = self.initialization_map.get(symbol)
        if not item:
            raise ValueError(f"Unknown type symbol: {symbol}")

        item_type, item_display_value = item
        return item_type(coord, self, symbol), item_display_value

    def visualize_map(self, mode: str = "emoji") -> None:
        """Generate the user-facing visualization of the Grid.

        Args:
            mode (str): The display mode

        """
        for r in range(self.__map_rows):
            for c in range(self.__map_cols):
                obj_in_coord = self.get_obj_in_coord(r, c)
                if not obj_in_coord:
                    self.__grid_user_display[r][c] = "　" if mode == "emoji" else "."
                else:
                    self.__grid_user_display[r][c] = self.get_display_symbol_of_obj(
                        obj_in_coord,
                        mode,
                    )

    def get_vis_map_as_str(self, mode: str = "ascii") -> str:
        """Return the visualization of the Grid as a multi-line string.

        Args:
            mode (str): The display mode

        Returns:
            A single string composed of the visualization rows joined by newline.

        """
        self.visualize_map(mode)
        return "\n".join("".join(row) for row in self.__grid_user_display)

    def render(self, p: Entity) -> ExitCodes:
        """Print the Grid and GUI, and return True if the game has ended.

        Args:
            p (Entity): The Player object in the current Grid instance

        Returns:
            True if the player has won or lost (game ended), otherwise False.

        """
        total_mushrooms = self.get_total_mushrooms()
        mushrooms_collected = p.get_mushroom_count()
        below = p.get_entity_below()
        item_here = below.__class__.__name__ if below else "Empty Tile"
        held_item_obj = p.get_item()
        held_item = held_item_obj.__class__.__name__ if held_item_obj else "Nothing"

        win = mushrooms_collected == total_mushrooms
        lose = p.get_is_dead()

        self.visualize_map()
        # replaced cls with this because OS command was being treated as "potential for injection"
        print("\033[H\033[J", end="")

        for row in self.__grid_user_display:
            print("".join(row))

        print(f"\n{mushrooms_collected} out of {total_mushrooms} mushroom(s) collected")

        if win:
            print("You win!")
        elif lose:
            print("You lose...")
        else:
            print(
                f"[W] Up [A] Left [S] Down [D] Right [!] Reset\n"
                f"{item_here} is here\n"
                f"Holding: {held_item}\n"
                f"What will you do?",
                end="",
            )
        if win:
            return ExitCodes.VICTORY
        elif lose:
            return ExitCodes.DEFEAT
