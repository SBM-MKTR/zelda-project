import textwrap

import arcade

from gameview import GameView
from map import Map


_MAP_TWO_TELEPORTERS = textwrap.dedent("""\
    width: 10
    height: 5
    teleporters:
    - id: tp1
      x: 2
      y: 3
      target_id: tp2
    - id: tp2
      x: 7
      y: 3
      target_id: tp1
    ---
    xxxxxxxxxx
    x T    T x
    x        x
    x   P    x
    xxxxxxxxxx
    ---
""")


def test_teleporter_moves_player_to_destination(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_TWO_TELEPORTERS)
    view = GameView(game_map)
    window.show_view(view)

    tp1_sprite = next(s for s, c in view.level.teleporter_infos if c.id == "tp1")
    tp2_sprite = next(s for s, c in view.level.teleporter_infos if c.id == "tp2")

    view.player.center_x = tp1_sprite.center_x
    view.player.center_y = tp1_sprite.center_y
    view.on_update(1 / 60)

    assert view.player.center_x == tp2_sprite.center_x
    assert view.player.center_y == tp2_sprite.center_y


def test_teleporter_cooldown_prevents_immediate_return(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_TWO_TELEPORTERS)
    view = GameView(game_map)
    window.show_view(view)

    tp1_sprite = next(s for s, c in view.level.teleporter_infos if c.id == "tp1")
    tp2_sprite = next(s for s, c in view.level.teleporter_infos if c.id == "tp2")

    view.player.center_x = tp1_sprite.center_x
    view.player.center_y = tp1_sprite.center_y
    view.on_update(1 / 60)

    assert view.player.center_x == tp2_sprite.center_x

    # Player is now on tp2 which targets tp1; cooldown should prevent immediate return
    view.on_update(1 / 60)

    assert view.player.center_x == tp2_sprite.center_x
