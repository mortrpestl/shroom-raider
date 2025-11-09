import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid


@pytest.fixture
def test_grid():
    """
    Provide a 3x3 test grid for Mushroom behavior.
    """
    map_data = """
...
...
...
"""
    return Grid("mushroom_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid):
    ENTITIES = import_entities({"Player", "Mushroom"})
    """
    Verify Mushroom is constructed correctly with proper flags.

    Verify:
    * Mushroom stores its position and grid reference correctly.
    * _is_collectable flag is True.
    * _is_collideable flag is False.
    """
    g = test_grid
    mush = ENTITIES["Mushroom"]([1, 1], g)
    g.add_layer_to_coord(1, 1, mush)

    assert mush.get_pos() == [1, 1]
    assert mush.get_on_grid() == g
    assert mush.get_collectable() is True
    assert mush.get_collideable() is False


def test_mushroom_collect_increments_player_count_and_disappears_from_grid(test_grid):
    ENTITIES = import_entities({"Player", "Mushroom"})
    """
    Verify collecting a Mushroom affects the player and grid correctly.

    Verify:
    * Player's mushroom count increments when Mushroom is collected.
    * Mushroom is removed from the grid after collection.
    * Player remains in the same grid cell.
    """
    g = test_grid
    mush = ENTITIES["Mushroom"]([1, 1], g)
    player = ENTITIES["Player"]([1, 1], g)
    g.add_layer_to_coord(1, 1, mush)
    g.add_layer_to_coord(1, 1, player)

    initial_count = player.get_mushroom_count()
    player.collect_shroom()

    assert player.get_mushroom_count() == initial_count + 1
    layers = g.get_layers_from_coord(1, 1)
    assert mush not in layers
    assert player in layers
