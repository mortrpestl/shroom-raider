import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid

# Register entities
ENTITIES = import_entities({"Player", "Axe", "Tree"})


@pytest.fixture
def test_grid():
    map_data = """.....
.....
..L..
.....
....."""
    return Grid("axe_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid):
    """
    * Verify: Axe initializes with correct position and flags
    """
    g = test_grid
    axe = ENTITIES["Axe"]([0, 0], g)
    assert axe.get_pos() == [0, 0]
    assert axe.get_on_grid() == g
    assert axe._is_collectable == True
    assert axe._is_collideable == False


def test_player_can_collect_axe(test_grid):
    """
    * Verify: Player can move onto Axe and collect it, removing it from the grid
    """
    g = test_grid
    player = g.get_player()
    axe = ENTITIES["Axe"]([2, 3], g)
    g.add_layer_to_coord(2, 3, axe)

    player.set_pos("d")
    player.collect_item()

    assert player.get_item() == axe
    layers = g.get_layers_from_coord(*player.get_pos())
    assert all(obj != ENTITIES["Axe"] or obj is player for obj in layers)


def test_player_uses_axe_on_tree(test_grid):
    """
    * Verify: Player uses Axe on a Tree, tree is removed, Axe is consumed
    """
    g = test_grid
    player = g.get_player()
    axe = ENTITIES["Axe"]([0, 0], g)
    player.set_item(axe)

    tree = ENTITIES["Tree"]([2, 3], g)
    g.add_layer_to_coord(2, 3, tree)

    result = player.set_pos("d")
    assert result == True
    assert g.get_obj_in_coord(2, 3) != tree
    assert player.get_item() is None


def test_player_tries_to_use_axe_on_two_trees(test_grid):
    """
    * Verify: Player with Axe can only chop one Tree at a time, Axe is consumed after first
    """
    g = test_grid
    player = g.get_player()
    axe = ENTITIES["Axe"]([0, 0], g)
    player.set_item(axe)

    tree1 = ENTITIES["Tree"]([2, 3], g)
    tree2 = ENTITIES["Tree"]([2, 4], g)
    g.add_layer_to_coord(2, 3, tree1)
    g.add_layer_to_coord(2, 4, tree2)

    # Move right to first tree
    result = player.set_pos("d")
    assert result == True
    assert g.get_obj_in_coord(2, 3) != tree1
    assert player.get_item() is None

    # Attempt to move right to second tree without another Axe
    result2 = player.set_pos("d")
    assert result2 == False
    # Tree2 should remain
    assert g.get_obj_in_coord(2, 4) == tree2
