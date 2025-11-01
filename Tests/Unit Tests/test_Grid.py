import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid



ENTITIES = import_entities({"Player","Tree","Mushroom","Rock","Water","PavedTile","Axe","Flamethrower"})


@pytest.fixture
def small_grid():
    map_data = """
L..
.T.
..+
"""
    return Grid("test_grid", map_data)

def test_grid_initialization(small_grid):
    grid = small_grid
    player = grid.get_player()
    assert isinstance(player, ENTITIES["Player"])
    assert player.get_pos() == (0, 0)

    #check tree exists at (1,1)
    obj = grid.get_obj_in_coord(1, 1)
    assert isinstance(obj, ENTITIES["Tree"])

    #check mushroom exists at (2,2)
    obj = grid.get_obj_in_coord(2, 2)
    assert isinstance(obj, ENTITIES["Mushroom"])

def test_add_and_pop_layer(small_grid):
    grid = small_grid
    player = grid.get_player()
    r,c = player.get_pos()

    #add a rock on top of player
    rock = ENTITIES["Rock"]([r,c], grid, 'R')
    grid.add_layer_to_coord(r,c, rock)
    layers = grid.get_layers_from_coord(r,c)
    assert layers[-1] == rock

    #pop the rock
    popped = grid.pop_layer_from_coord(r,c)
    assert popped == rock
    assert grid.get_layers_from_coord(r,c)[-1] == player

def test_get_vis_map_as_str(small_grid):
    grid = small_grid
    vis_str = grid.get_vis_map_as_str()
    #check that the returned string has correct rows
    rows = vis_str.splitlines()
    assert len(rows) == 3
    #top-left should be player symbol
    assert "L" in rows[0]

def test_level_clear_flag(small_grid):
    grid = small_grid
    assert not grid.get_is_cleared()
    grid.level_clear()
    assert grid.get_is_cleared()
