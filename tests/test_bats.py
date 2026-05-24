import arcade

import pytest

from map import GridCell, Map, BatBounds, bat_bounds
from gameview import GameView
from constants import TILE_SIZE


def test_bat_bounds() -> None:
    text = """width: 8
height: 8
---
xxxxxxxx





x  v  xx
xP     x
---
"""
    game_map = Map.from_string(text)

    assert game_map.get(3, 1) == GridCell.BAT
    assert bat_bounds(game_map, 3, 1, 70) == BatBounds(
        center_x=3 * TILE_SIZE + TILE_SIZE // 2,
        center_y=1 * TILE_SIZE + TILE_SIZE // 2,
        radius=70,
    )


def test_bats_bounds_raises_on_non_bat() -> None:
    text = """width: 4
height: 4
---
xxxx
xP x
x  x
xxxx
---
"""
    game_map = Map.from_string(text)

    with pytest.raises(ValueError):
        bat_bounds(game_map, 1, 1, 70)


def test_bats_dies_when_hit_by_boomerang(window: arcade.Window) -> None:
    text = """width: 5
height: 5
---
xxxxx
x P x
x v x
xxxxx
xxxxx
---
"""
    game_map = Map.from_string(text)
    view = GameView(game_map)
    window.show_view(view)

    initial = len(view.bats)

    view.on_key_press(arcade.key.D, 0)

    for _ in range(60):
        view.on_update(1/60)

    assert len(view.bats) == initial - 1

def test_bat_kills_player(window: arcade.Window) -> None:
    text = """width: 5
height: 5
---
xxxxx
x v x
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
