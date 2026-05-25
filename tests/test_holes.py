import pytest

import arcade

from map import Map
from map_types import GridCell
from gameview import GameView



def test_hole_kills_player_when_he_falls(window: arcade.Window) -> None:
    text = """width: 6
height: 6
---
xxxxxx
x O  x
x    x
x P  x
xxxxxx
xxxxxx
---
"""

    game_map = Map.from_string(text)
    assert game_map.get(2, 4) == GridCell.HOLE
    view = GameView(game_map)
    window.show_view(view)

    view.on_key_press(arcade.key.UP, 0)

    for _ in range(60):
        view.on_update(1/60)

    assert window.current_view is not view
