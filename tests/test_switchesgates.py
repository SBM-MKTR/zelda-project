import textwrap

import arcade

from boomerang import BoomerangState
from gameview import GameView
from map import Map
from player import Direction
from textures import TEXTURE_GATE_CLOSED, TEXTURE_GATE_OPEN, TEXTURE_SWITCH_OFF, TEXTURE_SWITCH_ON


_MAP_SWITCH_ONLY = textwrap.dedent("""\
    width: 8
    height: 5
    switches:
    - id: sw1
      x: 5
      y: 2
    ---
    xxxxxxxx
    x      x
    x P  ^ x
    x      x
    xxxxxxxx
    ---
""")

_MAP_SWITCH_AND_GATE = textwrap.dedent("""\
    width: 8
    height: 5
    switches:
    - id: sw1
      x: 5
      y: 2
    gates:
    - x: 6
      y: 2
      open_if:
        switch_is_on: sw1
    ---
    xxxxxxxx
    x      x
    x P  ^|x
    x      x
    xxxxxxxx
    ---
""")

_MAP_SWITCH_INITIALLY_ON = textwrap.dedent("""\
    width: 8
    height: 5
    switches:
    - id: sw1
      x: 5
      y: 2
      state: on
    gates:
    - x: 6
      y: 2
      open_if:
        switch_is_on: sw1
    ---
    xxxxxxxx
    x      x
    x P  ^|x
    x      x
    xxxxxxxx
    ---
""")

_MAP_GATE_NOT_FORMULA = textwrap.dedent("""\
    width: 8
    height: 5
    switches:
    - id: sw1
      x: 5
      y: 2
    gates:
    - x: 6
      y: 2
      open_if:
        not:
        - switch_is_on: sw1
    ---
    xxxxxxxx
    x      x
    x P  ^|x
    x      x
    xxxxxxxx
    ---
""")



def test_switch_is_initially_off(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_ONLY)
    view = GameView(game_map)
    window.show_view(view)

    assert view.switches[0].texture == TEXTURE_SWITCH_OFF


def test_switch_toggles_on_boomerang_hit(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_ONLY)
    view = GameView(game_map)
    window.show_view(view)

    view.player.direction = Direction.EAST
    view.on_key_press(arcade.key.D, 0)

    for _ in range(120):
        view.on_update(1 / 60)

    assert view.switches[0].texture == TEXTURE_SWITCH_ON


def test_gate_is_initially_closed(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_AND_GATE)
    view = GameView(game_map)
    window.show_view(view)

    gate = view.gate_system.gate_infos[0][0]
    assert gate in view.walls


def test_gate_opens_when_switch_toggled(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_AND_GATE)
    view = GameView(game_map)
    window.show_view(view)

    gate = view.gate_system.gate_infos[0][0]

    view.player.direction = Direction.EAST
    view.on_key_press(arcade.key.D, 0)

    for _ in range(120):
        view.on_update(1 / 60)

    assert gate not in view.walls


def test_gate_initially_open_when_switch_is_on(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_INITIALLY_ON)
    view = GameView(game_map)
    window.show_view(view)

    gate = view.gate_system.gate_infos[0][0]
    assert gate not in view.walls


def test_gate_with_not_formula_initially_open(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_GATE_NOT_FORMULA)
    view = GameView(game_map)
    window.show_view(view)

    gate = view.gate_system.gate_infos[0][0]
    assert gate not in view.walls


def test_gate_blocks_player(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_AND_GATE)
    view = GameView(game_map)
    window.show_view(view)

    gate = view.gate_system.gate_infos[0][0]

    view.on_key_press(arcade.key.RIGHT, 0)
    for _ in range(120):
        view.on_update(1 / 60)

    assert view.player.center_x < gate.center_x


def test_boomerang_toggles_switch_while_returning(window: arcade.Window) -> None:
    game_map = Map.from_string(_MAP_SWITCH_ONLY)
    view = GameView(game_map)
    window.show_view(view)

    switch = view.switches[0]

    view.boomerang.state = BoomerangState.RETURNING
    view.boomerang.center_x = switch.center_x
    view.boomerang.center_y = switch.center_y

    view.on_update(1 / 60)

    assert switch.texture == TEXTURE_SWITCH_ON
