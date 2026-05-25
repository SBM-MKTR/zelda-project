import pytest

from map import GridCell, InvalidMapFileException, Map


def test_from_string_valid_map() -> None:
    text = """width: 4
height: 3
---
x  *
 P
  sS
---
"""

    game_map = Map.from_string(text)

    assert game_map.width == 4
    assert game_map.height == 3
    assert game_map.player_start_x == 1
    assert game_map.player_start_y == 1

    assert game_map.get(0, 2) == GridCell.BUSH
    assert game_map.get(3, 2) == GridCell.CRYSTAL
    assert game_map.get(2, 0) == GridCell.SPINNER_HORIZONTAL
    assert game_map.get(3, 0) == GridCell.SPINNER_VERTICAL
    assert game_map.get(1, 1) == GridCell.PLAYER_START


def test_from_string_pads_short_rows_with_spaces() -> None:
    text = """width: 5
height: 2
---
P
xx
---
"""

    game_map = Map.from_string(text)

    assert game_map.get(0, 1) == GridCell.PLAYER_START
    assert game_map.get(4, 1) == GridCell.GRASS
    assert game_map.get(0, 0) == GridCell.BUSH
    assert game_map.get(1, 0) == GridCell.BUSH
    assert game_map.get(4, 0) == GridCell.GRASS


def test_from_string_rejects_missing_player() -> None:
    text = """width: 3
height: 2
---
xxx
***
---
"""

    with pytest.raises(InvalidMapFileException):
        Map.from_string(text)


def test_from_string_rejects_multiple_players() -> None:
    text = """width: 3
height: 2
---
P
 P
---
"""

    with pytest.raises(InvalidMapFileException):
        Map.from_string(text)


def test_from_string_rejects_row_too_long() -> None:
    text = """width: 3
height: 1
---
xxxx
---
"""

    with pytest.raises(InvalidMapFileException):
        Map.from_string(text)


def test_from_string_rejects_invalid_character() -> None:
    text = """width: 3
height: 1
---
P@x
---
"""

    with pytest.raises(InvalidMapFileException):
        Map.from_string(text)

def test_player_start_cell_is_stored_in_grid() -> None:
    """La cellule de départ du joueur doit être GridCell.PLAYER_START dans la grille."""
    text = """width: 3
height: 3
---
xxx
xPx
xxx
---
"""
    game_map = Map.from_string(text)
    assert game_map.player_start_x == 1
    assert game_map.player_start_y == 1
    assert game_map.get(1, 1) == GridCell.PLAYER_START
