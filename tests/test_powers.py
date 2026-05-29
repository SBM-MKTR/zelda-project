import textwrap
import arcade
from gameview import GameView
from map import Map
from power_system import FreezePower, GhostPower, PowerSystem
from constants import GHOST_ALPHA, POWER_DURATION_FRAMES

_MAP_WITH_SPINNER = textwrap.dedent("""\
    width: 8
    height: 5
    ---
    xxxxxxxx
    x      x
    x  s   x
    x P    x
    xxxxxxxx
    ---
""")

_MAP_WITH_ENEMY = textwrap.dedent("""\
    width: 8
    height: 5
    ---
    xxxxxxxx
    x      x
    x      x
    x Pv   x
    xxxxxxxx
    ---
""")

def _make_view(window: arcade.Window, map_text: str) -> GameView:
    game_map = Map.from_string(map_text)
    view = GameView(game_map)
    window.show_view(view)
    return view


def test_ghost_on_activate_sets_alpha(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_ENEMY)
    power = GhostPower()
    power.on_activate(view.player, [])
    assert view.player.alpha == GHOST_ALPHA


def test_ghost_on_deactivate_restores_alpha(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_ENEMY)
    power = GhostPower()
    power.on_activate(view.player, [])
    power.on_deactivate(view.player, [])
    assert view.player.alpha == 255


def test_power_system_starts_inactive(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_ENEMY)
    assert not view.power_system.is_ghost_active
    assert not view.power_system.is_frozen_active
    assert view.power_system.active_power_name is None


def test_power_expires_after_duration(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_ENEMY)
    view.power_system._active_power = GhostPower()
    view.power_system._remaining_frames = POWER_DURATION_FRAMES

    for _ in range(POWER_DURATION_FRAMES):
        view.power_system.update()

    assert not view.power_system.is_ghost_active
    assert view.power_system.active_power_name is None


def test_activating_new_power_deactivates_previous(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_ENEMY)
    view.power_system._active_power = GhostPower()
    view.power_system._active_power.on_activate(view.player, [])
    view.power_system._remaining_frames = POWER_DURATION_FRAMES

    view.power_system._active_power.on_deactivate(view.player, [])
    view.power_system._active_power = FreezePower()
    view.power_system._active_power.on_activate(view.player, [])

    assert not view.power_system.is_ghost_active
    assert view.power_system.is_frozen_active
    assert view.player.alpha == 255


def test_ghost_makes_player_invincible(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_ENEMY)
    view.power_system._active_power = GhostPower()
    view.power_system._remaining_frames = 60

    bat_sprite = view.bats[0]
    view.player.center_x = bat_sprite.center_x
    view.player.center_y = bat_sprite.center_y
    view.on_update(1 / 60)

    assert window.current_view is view


def test_freeze_stops_enemies(window: arcade.Window) -> None:
    view = _make_view(window, _MAP_WITH_SPINNER)
    view.power_system._active_power = FreezePower()
    view.power_system._remaining_frames = 60

    spinner = view.spinners[0]
    x_before = spinner.center_x
    view.on_update(1 / 60)

    assert spinner.center_x == x_before
