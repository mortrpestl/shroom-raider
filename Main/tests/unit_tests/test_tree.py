import sys
from pathlib import Path

import pytest
from classes.entities.import_entities import import_entities
from classes.grid import Grid

sys.path.append((Path(__file__).parent / "../..").resolve())

ENTITIES = import_entities({"Player", "Tree", "Mushroom", "Rock", "Water", "PavedTile", "Axe", "Flamethrower"})


@pytest.fixture
def large_grid():
    """Provide an empty 5x5 grid for testing Tree behavior.

    Returns:
        A test grid for testing.

    """
    map_data = """
.....
.....
.....
.....
.....
"""
    return Grid("large_tree_grid", map_data)


def test_initialization_stores_position_and_flags(large_grid: Grid):
    """Verify tree construction and basic attributes.

    - Create a Tree at a specific coordinate on an empty grid.
    - Ensure Tree stores its position and grid reference.
    - Assert Tree flags (_is_collideable, _is_burnable) are set.
    """
    g = large_grid
    tree = ENTITIES["Tree"]((0, 1), g)
    g.add_layer_to_coord(0, 1, tree)

    assert tree.get_pos() == [0, 1]
    assert tree.get_on_grid() == g
    assert tree.get_collideable()
    assert tree.get_burnable()


def test_tree_chop_removes_tree_from_grid(large_grid: Grid):
    """Ensure chopping a tree removes it from the grid.

    - Place a Tree at a grid cell.
    - Verify the top object is the Tree.
    - Call chop() and confirm the cell is cleared (None).
    """
    g = large_grid
    tree = ENTITIES["Tree"]((0, 1), g)
    g.add_layer_to_coord(0, 1, tree)

    assert g.get_obj_in_coord(0, 1) == tree
    tree.chop()
    assert g.get_obj_in_coord(0, 1) is None


def test_tree_burn_only_affects_adjacent_orthogonal_trees(large_grid: Grid):
    """Burning affects only orthogonally adjacent trees.

    - Place several Trees: two adjacent, one diagonal, one distant.
    - Burn the first Tree.
    - Verify:
      * Adjacent Tree is destroyed.
      * Diagonal Tree remains.
      * Distant Tree remains.
    """
    g = large_grid
    tree1 = ENTITIES["Tree"]((0, 1), g)
    g.add_layer_to_coord(0, 1, tree1)
    tree2 = ENTITIES["Tree"]((1, 1), g)
    g.add_layer_to_coord(1, 1, tree2)
    tree3 = ENTITIES["Tree"]((1, 3), g)
    g.add_layer_to_coord(1, 3, tree3)
    tree4 = ENTITIES["Tree"]((3, 3), g)
    g.add_layer_to_coord(3, 3, tree4)

    tree1.burn_connected()

    assert g.get_obj_in_coord(0, 1) is None
    assert g.get_obj_in_coord(1, 1) is None
    assert g.get_obj_in_coord(1, 3) == tree3
    assert g.get_obj_in_coord(3, 3) == tree4


def test_tree_burn_following_orthogonal_chain_only(large_grid: Grid):
    """Burning follows orthogonal chains only.

    - Create a chain of Trees: first two orthogonally connected, next ones diagonal.
    - Burn from the first Tree.
    - Verify:
      * Orthogonally connected Trees are removed.
      * Diagonally positioned Trees remain.
    """
    g = large_grid
    positions = [(0, 1), (1, 1), (2, 2), (3, 3)]
    trees = []
    for r, c in positions:
        t = ENTITIES["Tree"]((r, c), g)
        g.add_layer_to_coord(r, c, t)
        trees.append(t)

    trees[0].burn_connected()

    assert g.get_obj_in_coord(0, 1) is None
    assert g.get_obj_in_coord(1, 1) is None
    assert g.get_obj_in_coord(2, 2) == trees[2]
    assert g.get_obj_in_coord(3, 3) == trees[3]
