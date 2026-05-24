import arcade

from gameview import GameView

from map import *

def test_collect_crystals(window: arcade.Window) -> None:
    text = """width: 10
height: 10
---
xxxxxxxxxx






       *
P *     *x
xxxxxxxxxx
---
"""
    game_map = Map.from_string(text)
    view = GameView(game_map)
    window.show_view(view)

    INITIAL_CRYSTAL_COUNT = 3

    # Make sure we have the amount of coins we expect at the start
    assert len(view.crystals) == INITIAL_CRYSTAL_COUNT

    # Start moving right
    view.on_key_press(arcade.key.RIGHT, 0)

    # Let the game run for 1 second
    window.test(60)

    # We should have collected the first coin
    assert len(view.crystals) == INITIAL_CRYSTAL_COUNT - 1

    # Stop moving right, move up
    view.on_key_release(arcade.key.RIGHT, 0)
    view.on_key_press(arcade.key.UP, 0)

    # Let the game run for 1 more second
    window.test(60)

    # We should have collected the second coin
    assert len(view.crystals) == INITIAL_CRYSTAL_COUNT - 2
