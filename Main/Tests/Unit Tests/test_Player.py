import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid

# Register entities
ENTITIES = import_entities({"Player", "Axe", "Flamethrower", "Mushroom", "Water", "Tree"})

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
    return Grid("player_test_grid", map_data)

def test_initialization_stores_position_and_flags(test_grid):
    """
    * Verify: Player initializes with no item, zero mushrooms, and alive status
    """
    g = test_grid
    player = g.get_player()
    assert player.get_item() == None
    assert player.get_mushroom_count() == 0
    assert player.get_is_dead() == 0

def test_set_and_use_item(test_grid):
    """
    * Verify: Player can set an item and use it, clearing it afterwards
    """
    g = test_grid
    player = g.get_player()
    axe = ENTITIES["Axe"]([0, 0], g)
    player.set_item(axe)
    assert player.get_item() == axe
    player.use_item()
    assert player.get_item() == None

def test_increment_mushroom_count(test_grid):
    """
    * Verify: Mushroom count increments correctly
    """
    g = test_grid
    player = g.get_player()
    player.increment_mushroom_count()
    player.increment_mushroom_count()
    assert player.get_mushroom_count() == 2

def test_kill_sets_is_dead_flag(test_grid):
    """
    * Verify: Player kill() sets is_dead flag to 1
    """
    g = test_grid
    player = g.get_player()
    player.kill()
    assert player.get_is_dead() == 1

def test_get_above_item_returns_item(test_grid):
    """
    * Verify: get_above_item() returns an Axe or Flamethrower Entity if present beneath Player
    """
    g = test_grid
    player = g.get_player()
    axe = ENTITIES["Axe"](player.get_pos(), g)
    g.add_layer_to_coord(*player.get_pos(), axe)
    g.add_layer_to_coord(*player.get_pos(), player)
    result = player.get_above_item()
    assert isinstance(result, ENTITIES["Axe"]) or isinstance(result, ENTITIES["Flamethrower"])

def test_get_above_item_returns_false_when_not_collectible(test_grid):
    """
    * Verify: get_above_item() returns False when no item beneath Player
    """
    g = test_grid
    player = g.get_player()
    assert player.get_above_item() == False

def test_get_above_mushroom_returns_object(test_grid):
    """
    * Verify: get_above_mushroom() returns Mushroom instance if present beneath Player
    """
    g = test_grid
    player = g.get_player()
    shroom = ENTITIES["Mushroom"](player.get_pos(), g)
    g.add_layer_to_coord(*player.get_pos(), shroom)
    g.add_layer_to_coord(*player.get_pos(), player)
    result = player.get_above_mushroom()
    assert isinstance(result, ENTITIES["Mushroom"])

def test_get_above_mushroom_returns_false_if_none(test_grid):
    """
    * Verify: get_above_mushroom() returns False when no Mushroom beneath Player
    """
    g = test_grid
    player = g.get_player()
    assert player.get_above_mushroom() == False

def test_get_above_water_returns_true(test_grid):
    """
    * Verify: get_above_water() returns True when Water is beneath Player
    """
    g = test_grid
    player = g.get_player()
    water = ENTITIES["Water"](player.get_pos(), g)
    g.add_layer_to_coord(*player.get_pos(), water)
    g.add_layer_to_coord(*player.get_pos(), player)
    assert player.get_above_water() == True

def test_get_above_water_returns_false_if_none(test_grid):
    """
    * Verify: get_above_water() returns False when no Water beneath Player
    """
    g = test_grid
    player = g.get_player()
    assert player.get_above_water() == False

def test_collect_item_adds_to_player_and_removes_from_grid(test_grid):
    """
    * Verify: collect_item() equips item beneath Player and removes it from the grid
    """
    g = test_grid
    player = g.get_player()
    axe = ENTITIES["Axe"](player.get_pos(), g)
    g.add_layer_to_coord(*player.get_pos(), axe)
    g.add_layer_to_coord(*player.get_pos(), player)
    player.collect_item()
    assert isinstance(player.get_item(), ENTITIES["Axe"])
    layers = g.get_layers_from_coord(*player.get_pos())
    assert all(obj != ENTITIES["Axe"] or obj is player for obj in layers)

def test_collect_item_does_nothing_if_no_item(test_grid):
    """
    * Verify: collect_item() does nothing when no collectible item beneath Player
    """
    g = test_grid
    player = g.get_player()
    player.collect_item()
    assert player.get_item() == None

def test_get_movement_validity_out_of_bounds(test_grid):
    """
    * Verify: Player cannot move out of grid boundaries
    """
    g = test_grid
    player = g.get_player()
    assert player.get_movement_validity("w", -1, 2) == False
    assert player.get_movement_validity("s", 5, 2) == False
    assert player.get_movement_validity("a", 2, -1) == False
    assert player.get_movement_validity("d", 2, 5) == False

def test_get_movement_validity_with_flamethrower(test_grid):
    """
    * Verify: Player with Flamethrower burns a Tree object in target cell
    * Verify: Target cell no longer contains the Tree
    * Verify: Flamethrower is consumed after use
    """
    g = test_grid
    player = g.get_player()
    tree = ENTITIES["Tree"]([2, 3], g)
    g.add_layer_to_coord(2, 3, tree)
    player.set_item(ENTITIES["Flamethrower"]([0, 0], g))

    result = player.get_movement_validity("d", 2, 3)
    assert result == True
    assert g.get_obj_in_coord(2, 3) != tree
    assert player.get_item() == None

def test_get_movement_validity_with_axe(test_grid):
    """
    * Verify: Player with Axe chops a Tree object in target cell
    * Verify: Target cell no longer contains the Tree
    * Verify: Axe is consumed after use
    """
    g = test_grid
    player = g.get_player()
    tree = ENTITIES["Tree"]([3, 2], g)
    g.add_layer_to_coord(3, 2, tree)
    player.set_item(ENTITIES["Axe"]([0, 0], g))

    result = player.get_movement_validity("s", 3, 2)
    assert result == True
    assert g.get_obj_in_coord(3, 2) != tree
    assert player.get_item() == None
