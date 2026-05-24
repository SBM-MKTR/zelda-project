import pytest

import arcade

from map import GridCell, Map, SpinnerBounds, spinner_bounds
from gameview import GameView


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

def test_spinner_bounds_when_already_blocked() -> None:
    text = """width: 5
height: 5
---
xxxxx
x P x
xxxxx
xxsxx
xxxxx
---
"""
    game_map = Map.from_string(text)

    assert game_map.get(2, 1) == GridCell.SPINNER_HORIZONTAL

    bounds = spinner_bounds(game_map, 2, 1)

    assert bounds == SpinnerBounds(
        min_x=2,
        max_x=2,
        min_y=1,
        max_y=1,
    )


def test_spinner_dies_when_hit_by_boomerang(window: arcade.Window) -> None:
    text = """width: 5
height: 5
---
xxxxx
x P x
x s x
xxxxx
xxxxx
---
"""
    game_map = Map.from_string(text)
    view = GameView(game_map)
    window.show_view(view)

    initial = len(view.spinners)

    view.on_key_press(arcade.key.D, 0)

    for _ in range(60):
        view.on_update(1/60)

    assert len(view.spinners) == initial - 1


def test_spinner_kills_player(window: arcade.Window) -> None:
    text = """width: 5
height: 5
---
xxxxx
x s x
x P x
xxxxx
xxxxx
---
"""
    game_map = Map.from_string(text)
    view = GameView(game_map)
    window.show_view(view)

    view.on_key_press(arcade.key.UP, 0)

    for _ in range(60):
        view.on_update(1/60)

    assert window.current_view is not view
