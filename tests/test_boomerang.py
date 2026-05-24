import arcade

import pytest

from gameview import GameView

from map import Map

from player import Direction

from boomerang import Boomerang, BoomerangState


def test_boomerang_launches_and_returns(window: arcade.Window) -> None:
    text = """width: 12
height: 12
---
xxxxxxxxxxxx
xP         x









xxxxxxxxxxxx
---
"""
    game_map = Map.from_string(text)
    view = GameView(game_map)
    window.show_view(view)
    assert view.boomerang.state == BoomerangState.INACTIVE

    view.player.direction = Direction.EAST

    view.on_key_press(arcade.key.D, 0)

    assert view.boomerang.state == BoomerangState.LAUNCHING
    assert view.boomerang.dir_x == 1
    assert view.boomerang.dir_y == 0

    while view.boomerang.state == BoomerangState.LAUNCHING:
        view.on_update(1/60)

    assert view.boomerang.state == BoomerangState.RETURNING

    while view.boomerang.state == BoomerangState.RETURNING:
        view.on_update(1/60)

    assert view.boomerang.state == BoomerangState.INACTIVE


def test_boomerang_changes_states_when_hitting(window: arcade.Window) -> None:
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

    view.on_key_press(arcade.key.D, 0)

    while view.boomerang.state == BoomerangState.LAUNCHING:
        view.on_update(1/60)

    assert view.boomerang.state == BoomerangState.RETURNING
    assert len(view.bats) == 0
