import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from classes.entities.import_entities import import_entities
from classes.grid import Grid

# Register entities
ENTITIES = import_entities({"Player", "Water"})


@pytest.fixture
def test_grid():
    """* Verify: Provides a 5x5 test grid with Player starting at (2,2).

    Returns:
        A test grid for testing.

    """
    map_data = """.....
.....
..L..
.....
....."""
    return Grid("water_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid: Grid):
    """* Verify: Water is not collideable, not collectable, and deadly."""
    water = ENTITIES["Water"]([0, 0], test_grid)
    assert not water.get_collideable()
    assert not water.get_collectable()
    assert water._is_deadly


def test_player_moving_into_water_is_deadly(test_grid: Grid):
    """* Verify: Player moving onto Water cell detects deadly interaction."""
    g = test_grid
    player = g.get_player()
    # Place Water right next to Player so movement hits it
    water = ENTITIES["Water"]([2, 3], g)
    g.add_layer_to_coord(2, 3, water)

    # Attempt move right
    result = player.set_pos("d")

    # Player should have moved but is now dead
    assert result
    assert player.get_pos() == [2, 3]  # matches Water's location
    assert player.get_is_dead()
