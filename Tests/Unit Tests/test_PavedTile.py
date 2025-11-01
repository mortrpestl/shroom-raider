import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from Classes.Entities.import_entities import import_entities
from Classes.Grid import Grid

# Register entities
import_entities({"Player", "Rock", "PavedTile"})


@pytest.fixture
def test_grid():
    map_data = """.....
..L..
..R..
.._..
.....
....."""

    return Grid("pavedtile_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid):
    """
    Tests if PavedTile properly renders in grid (along with other objects we will use for testing)
    """
    g = test_grid
    player = g.get_player()
    rock = g.get_obj_in_coord(2, 2)
    paved = g.get_obj_in_coord(3, 2)

    # Player
    assert player.get_pos() == [1, 2]
    assert player.get_on_grid() == g
    assert player.get_collideable() is False
    assert player.get_pushable(None) is False
    assert player.get_collectable() is False

    # Rock
    assert rock.get_pos() == [2, 2]
    assert rock.get_on_grid() == g
    assert rock.get_collideable() is True
    assert rock.get_pushable(player) is True
    assert rock.get_collectable() is False

    # PavedTile
    assert paved.get_pos() == [3, 2]
    assert paved.get_on_grid() == g
    assert paved.get_collideable() is False
    assert paved.get_pushable(None) is False
    assert paved.get_collectable() is False


def test_player_moves_over_and_off_pavedtile(test_grid):
    """
    Move the player around the rock and onto the paved tile, then back.
    """
    g = test_grid
    player = g.get_player()
    paved = g.get_obj_in_coord(3, 2)

    # path (r,c): (1,2) → (1,3) → (2,3) → (3,3) → (3,2)
    moved = player.set_pos(["d", "s", "s", "a"])
    assert moved is True
    assert player.get_pos() == [3, 2]

    # PavedTile remains under player
    layers = g.get_layers_from_coord(3, 2)
    assert paved in layers

    # Move back to start: reverse path
    moved = player.set_pos(["a", "w", "w", "d"])
    assert moved is True
    assert player.get_pos() == [1, 2]

    # PavedTile still intact
    assert g.get_obj_in_coord(3, 2) == paved


def test_player_pushes_rock_onto_pavedtile(test_grid):
    """
    Player pushes the rock one cell down onto the paved tile:
      - Player (1,2), Rock (2,2), Paved (3,2)
      - Move "s" should push Rock to (3,2) and Player to (2,2)
    """
    g = test_grid
    player = g.get_player()
    rock = g.get_obj_in_coord(2, 2)
    paved = g.get_obj_in_coord(3, 2)

    moved = player.set_pos(["s"])
    assert moved is True
    assert player.get_pos() == [2, 2]
    assert rock.get_pos() == [3, 2]

    # PavedTile remains under Rock
    layers = g.get_layers_from_coord(3, 2)
    assert paved in layers
    assert rock in layers


def test_rock_moves_off_pavedtile(test_grid):
    """
    After the Rock sits on the PavedTile, move it further down to (4,2).
    """
    g = test_grid
    player = g.get_player()
    rock = g.get_obj_in_coord(2, 2)
    paved = g.get_obj_in_coord(3, 2)

    # Push Rock onto PavedTile
    assert player.set_pos(["s"]) is True
    assert rock.get_pos() == [3, 2]

    # Move Rock further down manually
    moved = rock.set_pos(["s"])
    assert moved is True
    assert rock.get_pos() == [4, 2]

    # PavedTile remains
    assert g.get_obj_in_coord(3, 2) == paved
