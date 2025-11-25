import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid

ENTITIES = import_entities({"Player", "Flamethrower"})


@pytest.fixture
def test_grid():
    """Provide a 3x3 test grid for Flamethrower behavior."""
    map_data = """
...
...
...
"""
    return Grid("flamethrower_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid):
    """Verify Flamethrower construction and basic attributes.

    - Place a Flamethrower at a specific coordinate.
    - Confirm it stores its position and grid reference.
    - Assert _is_collectable and _is_collideable flags.
    """
    g = test_grid
    flame = ENTITIES["Flamethrower"]([1, 1], g)
    g.add_layer_to_coord(1, 1, flame)

    assert flame.get_pos() == [1, 1]
    assert flame.get_on_grid() == g
    assert flame.get_collectable() is True
    assert flame.get_collideable() is False


def test_flamethrower_in_grid_stack(test_grid):
    """Ensure Flamethrower can coexist in a stack and be retrieved.

    - Place a Flamethrower under a Player.
    - Verify it is the second layer from the top.
    """
    g = test_grid
    flame = ENTITIES["Flamethrower"]([1, 1], g)
    player = ENTITIES["Player"]([1, 1], g)
    g.add_layer_to_coord(1, 1, flame)
    g.add_layer_to_coord(1, 1, player)

    layers = g.get_layers_from_coord(1, 1)
    assert layers[-1] == player
    assert layers[-2] == flame


def test_flamethrower_collected_and_picked_up_by_player(test_grid):
    """Verify that Player can detect and pick up Flamethrower.

    Verify:
    * Place a Player above a Flamethrower.
    * Simulate collect action by popping layers.
    * Ensure Player acquires Flamethrower and grid updates correctly.
    """
    g = test_grid
    flame = ENTITIES["Flamethrower"]([1, 1], g)
    player = ENTITIES["Player"]([1, 1], g)
    g.add_layer_to_coord(1, 1, flame)
    g.add_layer_to_coord(1, 1, player)

    # simulate collection
    popped_player = g.pop_layer_from_coord(1, 1)
    popped_item = g.pop_layer_from_coord(1, 1)
    player.set_item(popped_item)
    g.add_layer_to_coord(1, 1, popped_player)

    assert player.get_item() == flame
    # The Flamethrower is no longer in the grid cell
    assert g.get_layers_from_coord(1, 1)[-1] == player
