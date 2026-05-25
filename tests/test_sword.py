import arcade

from constants import SWORD_ATTACK_DURATION
from gameview import GameView
from map import Map
from player import Direction
from textures import TEXTURE_SWITCH_ON
from weapon_system import ActiveWeapon


def test_sword_becomes_inactive_after_animation(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x P x
x   x
xxxxx
---
""")

    view = GameView(game_map)
    window.show_view(view)

    view.on_key_press(arcade.key.R, 0)
    assert view.weapon_system.active_weapon == ActiveWeapon.SWORD

    view.on_key_press(arcade.key.D, 0)
    assert view.weapon_system.sword_weapon.is_active()

    view.on_update(SWORD_ATTACK_DURATION + 0.01)

    assert not view.weapon_system.sword_weapon.is_active()


def test_sword_kills_bat(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x v x
x P x
xxxxx
---
""")

    view = GameView(game_map)
    window.show_view(view)

    view.player.direction = Direction.NORTH
    view.on_key_press(arcade.key.R, 0)
    view.on_key_press(arcade.key.D, 0)
    view.on_update(1 / 60)

    assert len(view.bats) == 0


def test_sword_collects_crystal(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x P*x
x   x
xxxxx
---
""")

    view = GameView(game_map)
    window.show_view(view)

    view.player.direction = Direction.EAST
    view.on_key_press(arcade.key.R, 0)
    view.on_key_press(arcade.key.D, 0)
    view.on_update(1 / 60)

    assert len(view.crystals) == 0
    assert view.score == 1


def test_sword_toggles_switch(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 5
height: 5
switches:
  - id: sw1
    x: 3
    y: 2
---
xxxxx
x   x
x P^x
x   x
xxxxx
---
""")

    view = GameView(game_map)
    window.show_view(view)

    view.player.direction = Direction.EAST
    view.on_key_press(arcade.key.R, 0)
    view.on_key_press(arcade.key.D, 0)
    view.on_update(1 / 60)

    assert view.switches[0].texture == TEXTURE_SWITCH_ON


def test_player_does_not_move_during_sword_attack(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x P x
x   x
xxxxx
---
""")

    view = GameView(game_map)
    window.show_view(view)

    view.on_key_press(arcade.key.R, 0)
    view.on_key_press(arcade.key.D, 0)

    old_x = view.player.center_x
    old_y = view.player.center_y

    view.on_key_press(arcade.key.RIGHT, 0)
    view.on_update(1 / 60)

    assert view.player.center_x == old_x
    assert view.player.center_y == old_y
