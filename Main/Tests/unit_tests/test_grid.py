import os
import sys

import pytest
from classes.entities.import_entities import import_entities
from classes.grid import Grid
from helper_classes import DummyPlayer, LosePlayer, WinPlayer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


ENTITIES = import_entities({"Player", "Tree", "Mushroom", "Rock", "Water", "PavedTile", "Axe", "Flamethrower"})


@pytest.fixture
def small_grid():
    map_data = """
L..
.T.
..+
"""
    return Grid("test_grid", map_data)


def test_initialization_stores_position_and_flags(small_grid):
    """Verify player, trees, and mushrooms are correctly placed on grid initialization."""
    g = small_grid
    player = g.get_player()
    assert isinstance(player, ENTITIES["Player"])
    assert player.get_pos() == [0, 0]
    assert isinstance(g.get_obj_in_coord(1, 1), ENTITIES["Tree"])
    assert isinstance(g.get_obj_in_coord(2, 2), ENTITIES["Mushroom"])


def test_layer_addition_and_removal_updates_top_layer(small_grid):
    """Ensure adding a layer places it on top, and popping restores the previous top layer."""
    g = small_grid
    p = g.get_player()
    r, c = p.get_pos()
    rock = ENTITIES["Rock"]([r, c], g, "R")
    g.add_layer_to_coord(r, c, rock)
    assert g.get_layers_from_coord(r, c)[-1] == rock
    assert g.pop_layer_from_coord(r, c) == rock
    assert g.get_layers_from_coord(r, c)[-1] == p


def test_visual_map_ascii_displays_correct_symbols(small_grid):
    """Verify ASCII visual map correctly represents objects on the grid."""
    g = small_grid
    vis = g.get_vis_map_as_str()
    rows = vis.splitlines()
    assert rows[0][0] == "L"
    assert rows[1][1] == "T"
    assert rows[2][2] == "+"


def test_visual_map_emoji_displays_correct_emojis(small_grid):
    """Verify emoji visual map correctly represents objects on the grid."""
    g = small_grid
    vis = g.get_vis_map_as_str(mode="emoji")
    rows = vis.splitlines()
    assert rows[0][0] == "🧑"
    assert rows[1][1] == "🌲"
    assert rows[2][2] == "🍄"


def test_level_clear_flag_updates_properly(small_grid):
    """Ensure calling level_clear sets the cleared flag on the grid."""
    g = small_grid
    assert not g.get_is_cleared()
    g.level_clear()
    assert g.get_is_cleared()


def test_get_obj_in_coord_raises_for_out_of_bounds(small_grid):
    """Verify that querying objects outside grid bounds raises IndexError."""
    g = small_grid
    with pytest.raises(IndexError):
        g.get_obj_in_coord(-1, 0)
    with pytest.raises(IndexError):
        g.get_obj_in_coord(0, 3)


def test_init_coord_creates_correct_objects_and_raises_for_invalid():
    """Verify init_coord produces correct objects and raises ValueError for unknown symbols."""
    g = Grid("tmp", "L.T\n.+.\nR~_")
    obj, _ = g.init_coord("L", [0, 0])
    assert isinstance(obj, ENTITIES["Player"])
    obj2, _ = g.init_coord("T", [0, 1])
    assert isinstance(obj2, ENTITIES["Tree"])
    with pytest.raises(ValueError):
        g.init_coord("Z", [0, 0])

    # ! previous version, changed because of refactor in Grid.
    # entities = ENTITIES
    # g = Grid("tmp", "L.T\n.+.\nR~_")
    # obj, _ = g.init_coord('L', (0, 0), entities)
    # assert isinstance(obj, entities["Player"])
    # obj2, _ = g.init_coord('T', (0, 1), entities)
    # assert isinstance(obj2, entities["Tree"])
    # with pytest.raises(ValueError):
    #     g.init_coord('Z', (0, 0), entities)


def test_get_display_symbol_returns_correct_ascii_and_emoji(small_grid):
    """Ensure get_display_symbol_of_obj returns ASCII, emoji, or None for unknown objects."""
    g = small_grid
    tree = ENTITIES["Tree"]((1, 1), g, "T")
    assert g.get_display_symbol_of_obj(tree, mode="emoji") in {"🌲"}
    assert g.get_display_symbol_of_obj(tree, mode="ascii") == "T"
    assert g.get_display_symbol_of_obj(object()) is None


def test_get_grid_by_name_returns_correct_instance_or_raises_keyerror(small_grid):
    """Verify get_grid_by_name returns the correct grid or raises KeyError for unknown names."""
    g = small_grid
    assert Grid.get_grid_by_name("test_grid") is g
    with pytest.raises(KeyError):
        Grid.get_grid_by_name("nonexistent")


def test_render_behavior_returns_expected_values(small_grid):
    """Verify render output for dummy, winning, and losing players."""
    g = small_grid
    assert not g.render(DummyPlayer(on_grid=g), test_mode=True)
    assert g.render(WinPlayer(on_grid=g), test_mode=True)
    assert g.render(LosePlayer(on_grid=g), test_mode=True)


def test_top_layer_object_returns_correct_layer_after_pop(small_grid):
    """Ensure get_obj_in_coord returns topmost object, correctly updated after adding/popping layers."""
    g = small_grid
    p = g.get_player()
    r, c = p.get_pos()
    rock = ENTITIES["Rock"]((r, c), g, "R")
    g.add_layer_to_coord(r, c, rock)
    assert g.get_obj_in_coord(r, c) is rock
    g.pop_layer_from_coord(r, c)
    assert g.get_obj_in_coord(r, c) is p
