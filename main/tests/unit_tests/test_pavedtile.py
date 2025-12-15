import sys
from pathlib import Path

import pytest
from classes.entities.import_entities import import_entities
from classes.grid import Grid

sys.path.append((Path(__file__).parent / "../..").resolve())

import_entities({"Player", "Rock", "PavedTile"})


@pytest.fixture
def test_grid() -> Grid:
    """Provide a 6x5 test grid with Player, Rock, and PavedTile for testing.

    Returns:
        Grid: A Grid instance with preset objects.

    """
    map_data = """.....
..L..
..R..
.._..
.....
....."""
    return Grid("pavedtile_test_grid", map_data)


def test_initialization_stores_position_and_flags(test_grid: Grid) -> None:
    """Test that PavedTile and other objects are correctly initialized on the grid."""
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


def test_player_moves_over_and_off_pavedtile(test_grid: Grid) -> None:
    """Move the player around the rock onto the paved tile, then back."""
    g = test_grid
    player = g.get_player()
    paved = g.get_obj_in_coord(3, 2)

    # path (r,c): (1,2) → (1,3) → (2,3) → (3,3) → (3,2)
    moved = False
    for inst in "dssa":
        moved = player.set_pos(inst)
    assert moved is True
    assert player.get_pos() == [3, 2]

    # PavedTile remains under player
    layers = g.get_layers_from_coord(3, 2)
    assert paved in layers

    # Move back to start: reverse path
    moved = False
    for inst in "awwd":
        moved = player.set_pos(inst)
    assert moved is True
    assert player.get_pos() == [1, 2]

    # PavedTile still intact
    assert g.get_obj_in_coord(3, 2) == paved


def test_player_pushes_rock_onto_pavedtile(test_grid: Grid) -> None:
    """Player pushes the rock one cell down onto the paved tile.

    - Player at (1,2), Rock at (2,2), PavedTile at (3,2).
    - Moving 's' pushes Rock to (3,2) and Player to (2,2).
    """
    g = test_grid
    player = g.get_player()
    rock = g.get_obj_in_coord(2, 2)
    paved = g.get_obj_in_coord(3, 2)

    moved = player.set_pos("s")
    assert moved is True
    assert player.get_pos() == [2, 2]
    assert rock.get_pos() == [3, 2]

    # PavedTile remains under Rock
    layers = g.get_layers_from_coord(3, 2)
    assert paved in layers
    assert rock in layers


def test_rock_moves_off_pavedtile(test_grid: Grid) -> None:
    """Move the rock further down from the PavedTile to (4,2)."""
    g = test_grid
    player = g.get_player()
    rock = g.get_obj_in_coord(2, 2)
    paved = g.get_obj_in_coord(3, 2)

    # Push Rock onto PavedTile
    assert player.set_pos("s") is True
    assert rock.get_pos() == [3, 2]

    # Move Rock further down manually
    moved = rock.set_pos("s")
    assert moved is True
    assert rock.get_pos() == [4, 2]

    # PavedTile remains
    assert g.get_obj_in_coord(3, 2) == paved
