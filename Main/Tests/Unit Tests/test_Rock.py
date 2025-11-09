import sys
import os
import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid
from helper_classes import DummyPlayer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

ENTITIES = import_entities({"Player", "Rock", "Water", "PavedTile", "Mushroom"})




@pytest.fixture
def test_grid():
    """
    Provide a 3x3 test grid for Rock behavior.
    Center [1,1] is empty.
    """
    map_data = """
...
...
...
"""
    return Grid("rock_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid):
    """
    Verify Rock construction and basic attributes.

    - Place a Rock at a specific coordinate.
    - Confirm Rock stores its position and grid reference.
    - Assert Rock flags (_is_collideable, _is_pushable, _is_collectable) are correct.
    """
    g = test_grid
    rock = ENTITIES["Rock"]([1, 1], g)
    g.add_layer_to_coord(1, 1, rock)

    assert rock.get_pos() == [1, 1]
    assert rock.get_on_grid() == g
    assert rock.get_collideable()
    assert rock.get_pushable(DummyPlayer())
    assert not rock.get_collectable()


def test_rock_push_into_empty_space_succeeds(test_grid):
    """
    Rock can be pushed by Player into an empty cell.

    - Place Rock at [1,1].
    - Attempt to move Rock downwards ('s').
    - Verify Rock moved to [2,1] and original cell is empty.
    """
    g = test_grid
    rock = ENTITIES["Rock"]([1, 1], g)
    g.add_layer_to_coord(1, 1, rock)

    moved = rock.set_pos("s")
    assert moved
    assert g.get_obj_in_coord(2, 1) == rock
    assert g.get_obj_in_coord(1, 1) is None


def test_rock_cannot_move_outside_grid(test_grid):
    """
    Rock cannot move outside the grid bounds.

    - Place Rock at top-left [0,0].
    - Attempt to move Rock up ('w') and left ('a').
    - Verify movement fails and position stays the same.
    """
    g = test_grid
    rock = ENTITIES["Rock"]([0, 0], g)
    g.add_layer_to_coord(0, 0, rock)

    moved = rock.set_pos("w")
    assert not moved
    assert rock.get_pos() == [0, 0]

    moved = rock.set_pos("a")
    assert not moved
    assert rock.get_pos() == [0, 0]


def test_rock_push_into_water_converts_to_paved_tile(test_grid):
    """
    Pushing Rock into Water replaces Water with PavedTile and destroys the Rock.

    - Place Rock at [1,1], Water at [2,1].
    - Move Rock down ('s').
    - Verify:
        * Water cell replaced with PavedTile.
        * Rock is destroyed (no longer in grid).
    """
    g = test_grid
    rock = ENTITIES["Rock"]([1, 1], g)
    water = ENTITIES["Water"]([2, 1], g)
    g.add_layer_to_coord(1, 1, rock)
    g.add_layer_to_coord(2, 1, water)

    moved = rock.set_pos("s")
    assert moved
    target_obj = g.get_obj_in_coord(2, 1)
    assert target_obj is not None
    assert target_obj.__class__.__name__ == "PavedTile"
    # Rock is destroyed
    assert g.get_obj_in_coord(1, 1) is None


def test_rock_push_invalid_blocked_by_collectable(test_grid):
    """
    Rock cannot move onto a collectable object.

    - Place a Rock and a collectable (e.g., Mushroom) below it.
    - Attempt to move Rock onto the collectable.
    - Verify movement fails and Rock remains in place.
    """
    g = test_grid
    rock = ENTITIES["Rock"]([1, 1], g)
    collectable = ENTITIES["Mushroom"]([2, 1], g)
    g.add_layer_to_coord(1, 1, rock)
    g.add_layer_to_coord(2, 1, collectable)

    moved = rock.set_pos("s")
    assert not moved
    assert g.get_obj_in_coord(1, 1) == rock
    assert g.get_obj_in_coord(2, 1) == collectable
