import textwrap

import arcade

from gameview import GameView
from map import Map


_MAP_KEY_CHEST = textwrap.dedent("""\
    width: 10
    height: 5
    keys:
    - id: key1
      x: 3
      y: 2
    - id: key2
      x: 5
      y: 2
    chests:
    - id: chest1
      x: 7
      y: 2
      key_id: key2
    ---
    xxxxxxxxxx
    x        x
    x  k k C x
    x P      x
    xxxxxxxxxx
    ---
""")


def test_key_is_collected_when_player_walks_over_it(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_KEY_CHEST)
    view = GameView(game_map)
    window.show_view(view)

    assert len(view.level.key_infos) == 2

    key1_sprite = next(s for s, c in view.level.key_infos if c.id == "key1")
    view.player.center_x = key1_sprite.center_x
    view.player.center_y = key1_sprite.center_y
    view.on_update(1 / 60)

    assert len(view.level.key_infos) == 1
    remaining_ids = {c.id for _, c in view.level.key_infos}
    assert "key1" not in remaining_ids


def test_chest_requires_key_to_open(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_KEY_CHEST)
    view = GameView(game_map)
    window.show_view(view)

    chest_sprite = next(s for s, c in view.level.chest_infos if c.id == "chest1")
    view.player.center_x = chest_sprite.center_x
    view.player.center_y = chest_sprite.center_y
    view.on_update(1 / 60)

    assert "key" in view.chest_message_text.text.lower()
    assert len(view.level.chest_infos) == 1


def test_chest_rejects_wrong_key(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_KEY_CHEST)
    view = GameView(game_map)
    window.show_view(view)

    # Collect key1 (wrong key for chest1 which needs key2)
    key1_sprite = next(s for s, c in view.level.key_infos if c.id == "key1")
    view.player.center_x = key1_sprite.center_x
    view.player.center_y = key1_sprite.center_y
    view.on_update(1 / 60)

    chest_sprite = next(s for s, c in view.level.chest_infos if c.id == "chest1")
    view.player.center_x = chest_sprite.center_x
    view.player.center_y = chest_sprite.center_y
    view.on_update(1 / 60)

    assert "wrong" in view.chest_message_text.text.lower()
    assert len(view.level.chest_infos) == 1


def test_correct_key_opens_chest_and_activates_power(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_KEY_CHEST)
    view = GameView(game_map)
    window.show_view(view)

    key2_sprite = next(s for s, c in view.level.key_infos if c.id == "key2")
    view.player.center_x = key2_sprite.center_x
    view.player.center_y = key2_sprite.center_y
    view.on_update(1 / 60)

    chest_sprite = next(s for s, c in view.level.chest_infos if c.id == "chest1")
    view.player.center_x = chest_sprite.center_x
    view.player.center_y = chest_sprite.center_y
    view.on_update(1 / 60)

    assert len(view.level.chest_infos) == 0
    assert view.power_system.active_power_name is not None
