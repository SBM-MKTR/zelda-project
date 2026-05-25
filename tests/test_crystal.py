import arcade

from gameview import GameView

from map import *

def test_collect_crystals(window: arcade.Window) -> None:
    text = """width: 5
height: 5
---
xxxxx
x   x
x * x
xP* x
xxxxx
---
"""
    game_map = Map.from_string(text)
    view = GameView(game_map)
    window.show_view(view)

    assert len(view.crystals) == 2

    first_crystal = view.crystals[0]
    view.player.center_x = first_crystal.center_x
    view.player.center_y = first_crystal.center_y
    view.on_update(1 / 60)

    assert len(view.crystals) == 1
    assert view.score == 1

    second_crystal = view.crystals[0]
    view.player.center_x = second_crystal.center_x
    view.player.center_y = second_crystal.center_y
    view.on_update(1 / 60)

    assert len(view.crystals) == 0
    assert view.score == 2
