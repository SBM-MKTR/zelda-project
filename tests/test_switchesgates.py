import textwrap

import arcade
import pytest

from boomerang import BoomerangState
from gameview import GameView
from map import Map
from map_parser import evaluate_formula
from player import Direction
from textures import TEXTURE_SWITCH_OFF, TEXTURE_SWITCH_ON


# ---------------------------------------------------------------------------
# Tests de evaluate_formula (sans Arcade, pure logique)
# ---------------------------------------------------------------------------

def test_formula_switch_is_on() -> None:
    formula = {"switch_is_on": "a"}
    assert evaluate_formula(formula, {"a": True}) is True
    assert evaluate_formula(formula, {"a": False}) is False


def test_formula_not() -> None:
    formula = {"not": [{"switch_is_on": "a"}]}
    assert evaluate_formula(formula, {"a": True}) is False
    assert evaluate_formula(formula, {"a": False}) is True


def test_formula_and() -> None:
    formula = {"and": [{"switch_is_on": "a"}, {"switch_is_on": "b"}]}
    assert evaluate_formula(formula, {"a": True,  "b": True})  is True
    assert evaluate_formula(formula, {"a": True,  "b": False}) is False
    assert evaluate_formula(formula, {"a": False, "b": True})  is False
    assert evaluate_formula(formula, {"a": False, "b": False}) is False


def test_formula_or() -> None:
    formula = {"or": [{"switch_is_on": "a"}, {"switch_is_on": "b"}]}
    assert evaluate_formula(formula, {"a": True,  "b": False}) is True
    assert evaluate_formula(formula, {"a": False, "b": True})  is True
    assert evaluate_formula(formula, {"a": False, "b": False}) is False


def test_formula_nested() -> None:
    # (a AND NOT b)
    formula = {
        "and": [
            {"switch_is_on": "a"},
            {"not": [{"switch_is_on": "b"}]},
        ]
    }
    assert evaluate_formula(formula, {"a": True,  "b": False}) is True
    assert evaluate_formula(formula, {"a": True,  "b": True})  is False
    assert evaluate_formula(formula, {"a": False, "b": False}) is False

# ---------------------------------------------------------------------------
# Tests d'intégration avec Arcade
# ---------------------------------------------------------------------------

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


def test_boomerang_toggles_switch_while_returning(window: arcade.Window) -> None:
    """Le boomerang peut activer un switch même en état RETURNING."""
    game_map = Map.from_string(_MAP_SWITCH_ONLY)
    view = GameView(game_map)
    window.show_view(view)

    switch = view.switches[0]

    # Place le boomerang en état RETURNING directement sur le switch
    view.boomerang.state = BoomerangState.RETURNING
    view.boomerang.center_x = switch.center_x
    view.boomerang.center_y = switch.center_y

    view.on_update(1 / 60)

    assert switch.texture == TEXTURE_SWITCH_ON
