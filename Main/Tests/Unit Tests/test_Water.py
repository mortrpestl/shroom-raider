import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid

# Register entities
ENTITIES = import_entities({"Player", "Water"})

@pytest.fixture
def test_grid():
    """
    * Verify: Provides a 5x5 test grid with Player starting at (2,2)
    """
    map_data = """.....
.....
..L..
.....
....."""
    return Grid("water_test_grid", map_data)

def test_initialization_stores_position_and_flags(test_grid):
    """
    * Verify: Water is not collideable, not collectable, and deadly
    """
    water = ENTITIES["Water"]([0, 0], test_grid)
    assert water.get_collideable() == False
    assert water.get_collectable() == False
    assert water._is_deadly == True

# def test_player_detects_water_above(test_grid):
#     """
#     * Verify: Player.get_above_water() returns True when Water is beneath Player
#     """
#     g = test_grid
#     player = g.get_player()
#     water = ENTITIES["Water"](player.get_pos(), g)
#     g.add_layer_to_coord(*player.get_pos(), water)
#     g.add_layer_to_coord(*player.get_pos(), player)
#     assert player.get_above_water() == True

# def test_player_no_water_above_returns_false(test_grid):
#     """
#     * Verify: Player.get_above_water() returns False when no Water beneath Player
#     """
#     g = test_grid
#     player = g.get_player()
#     assert player.get_above_water() == False

def test_player_moving_into_water_is_deadly(test_grid):
    """
    * Verify: Player moving onto Water cell detects deadly interaction
    """
    g = test_grid
    player = g.get_player()
    # Place Water right next to Player so movement hits it
    water = ENTITIES["Water"]([2, 3], g)
    g.add_layer_to_coord(2, 3, water)
    
    # Attempt move right
    result = player.set_pos("d")
    
    # Player should have moved but is now dead
    assert result == True
    assert player.get_pos() == [2, 3]   # matches Water's location
    assert player.get_is_dead() == True

