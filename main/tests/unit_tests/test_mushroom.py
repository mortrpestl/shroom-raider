import sys
from pathlib import Path

import pytest

sys.path.append((Path(__file__).parent / "../..").resolve())

from classes.entities.import_entities import import_entities
from classes.grid import Grid


@pytest.fixture
def test_grid() -> Grid:
    """Provide a 3x3 test grid for Mushroom behavior.

    Returns:
        Grid: A blank 3x3 grid for testing Mushroom placement and interactions.

    """
    map_data = """
...
...
...
"""
    return Grid("mushroom_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid: Grid) -> None:
    """Verify Mushroom is constructed correctly with proper flags.

    Steps:
        1. Mushroom stores its position and grid reference correctly.
        2. _is_collectable flag is True.
        3. _is_collideable flag is False.
    """
    entities = import_entities({"Player", "Mushroom"})
    g = test_grid
    mush = entities["Mushroom"]([1, 1], g)
    g.add_layer_to_coord(1, 1, mush)

    assert mush.get_pos() == [1, 1]
    assert mush.get_on_grid() == g
    assert mush.get_collectable() is True
    assert mush.get_collideable() is False


def test_mushroom_collect_increments_player_count_and_disappears_from_grid(test_grid: Grid) -> None:
    """Verify collecting a Mushroom affects the player and grid correctly.

    Steps:
        1. Player's mushroom count increments when Mushroom is collected.
        2. Mushroom is removed from the grid after collection.
        3. Player remains in the same grid cell.
    """
    entities = import_entities({"Player", "Mushroom"})
    g = test_grid
    mush = entities["Mushroom"]([1, 1], g)
    player = entities["Player"]([1, 1], g)
    g.add_layer_to_coord(1, 1, mush)
    g.add_layer_to_coord(1, 1, player)

    initial_count = player.get_mushroom_count()
    player.collect_shroom()

    assert player.get_mushroom_count() == initial_count + 1
    layers = g.get_layers_from_coord(1, 1)
    assert mush not in layers
    assert player in layers
