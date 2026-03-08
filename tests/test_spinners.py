import pytest

from map import GridCell, Map, SpinnerBounds, spinner_bounds


def test_horizontal_spinner_bounds() -> None:
    text = """width: 8
height: 3
---
xxxxxxxx
x  s  xx
xP     x
---
"""
    game_map = Map.from_string(text)

    assert game_map.get(3, 1) == GridCell.SPINNER_HORIZONTAL
    assert spinner_bounds(game_map, 3, 1) == SpinnerBounds(
        min_x=1,
        max_x=5,
        min_y=1,
        max_y=1,
    )


def test_vertical_spinner_bounds() -> None:
    text = """width: 5
height: 6
---
xxxxx
x S x
x   x
x   x
xP  x
xxxxx
---
"""
    game_map = Map.from_string(text)

    assert game_map.get(2, 4) == GridCell.SPINNER_VERTICAL
    assert spinner_bounds(game_map, 2, 4) == SpinnerBounds(
        min_x=2,
        max_x=2,
        min_y=1,
        max_y=4,
    )


def test_spinner_bounds_raises_on_non_spinner() -> None:
    text = """width: 4
height: 3
---
xxxx
xP x
xxxx
---
"""
    game_map = Map.from_string(text)

    with pytest.raises(ValueError):
        spinner_bounds(game_map, 1, 1)
