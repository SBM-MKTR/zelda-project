
import pytest
import arcade

from gate_system import GateSystem
from map_parser import evaluate_formula, validate_formula
from map_types import GateConfig, InvalidMapFileException
from textures import (
    TEXTURE_GATE_CLOSED,
    TEXTURE_GATE_OPEN,
    TEXTURE_SWITCH_OFF,
    TEXTURE_SWITCH_ON,
)


def _make_switch(on: bool = False) -> arcade.Sprite:
    sprite = arcade.Sprite()
    sprite.texture = TEXTURE_SWITCH_ON if on else TEXTURE_SWITCH_OFF
    return sprite


def _make_gate_system(
    switch_states: dict[str, bool],
    gate_formulas: list[tuple[arcade.Sprite, dict]],
) -> tuple[GateSystem, dict[str, arcade.Sprite]]:
    walls: arcade.SpriteList = arcade.SpriteList()
    gates_list: arcade.SpriteList = arcade.SpriteList()

    switch_sprites: dict[str, arcade.Sprite] = {}
    switch_infos = []
    for switch_id, state in switch_states.items():
        sprite = _make_switch(on=state)
        switch_sprites[switch_id] = sprite
        switch_infos.append((sprite, switch_id))

    gate_infos = []
    for gate_sprite, formula in gate_formulas:
        config = GateConfig(x=0, y=0, open_if=formula)
        walls.append(gate_sprite)
        gate_infos.append((gate_sprite, config))

    gs = GateSystem(
        switch_infos=switch_infos,
        gate_infos=gate_infos,
        walls=walls,
        gates=gates_list,
    )
    return gs, switch_sprites


def test_toggle_switch_changes_state() -> None:
    gs, switches = _make_gate_system({"a": False}, [])
    sw = switches["a"]

    gs.toggle_switch(sw)

    assert gs._switch_state_map[sw] is True
    assert sw.texture == TEXTURE_SWITCH_ON


def test_toggle_unknown_switch_raises() -> None:
    gs, _ = _make_gate_system({"a": False}, [])

    with pytest.raises(ValueError):
        gs.toggle_switch(_make_switch())


def test_gate_opens_when_formula_is_true() -> None:
    gate = _make_switch()
    gate.texture = TEXTURE_GATE_CLOSED
    gs, switches = _make_gate_system({"a": False}, [(gate, {"switch_is_on": "a"})])

    gs.toggle_switch(switches["a"])
    gs.update()

    assert gate not in gs.walls
    assert gate in gs.gates


def test_gate_closes_when_formula_becomes_false() -> None:
    gate = arcade.Sprite()
    gate.texture = TEXTURE_GATE_CLOSED
    gs, switches = _make_gate_system({"a": True}, [(gate, {"switch_is_on": "a"})])

    gs.update()
    gs.toggle_switch(switches["a"])
    gs.update()

    assert gate in gs.walls
    assert gate.texture == TEXTURE_GATE_CLOSED


def test_validate_unknown_switch_raises() -> None:
    with pytest.raises(InvalidMapFileException):
        validate_formula({"switch_is_on": "unknown"}, {"a"})


def test_validate_unknown_operator_raises() -> None:
    with pytest.raises(InvalidMapFileException):
        validate_formula({"xor": [{"switch_is_on": "a"}, {"switch_is_on": "b"}]}, {"a", "b"})


def test_validate_depth_limit_raises() -> None:
    formula: dict = {"switch_is_on": "a"}
    for _ in range(21):
        formula = {"not": [formula]}
    with pytest.raises(InvalidMapFileException):
        validate_formula(formula, {"a"})



def test_evaluate_not() -> None:
    formula = {"not": [{"switch_is_on": "a"}]}
    assert evaluate_formula(formula, {"a": True}) is False
    assert evaluate_formula(formula, {"a": False}) is True


def test_evaluate_and() -> None:
    formula = {"and": [{"switch_is_on": "a"}, {"switch_is_on": "b"}]}
    assert evaluate_formula(formula, {"a": True, "b": True}) is True
    assert evaluate_formula(formula, {"a": True, "b": False}) is False


def test_evaluate_or() -> None:
    formula = {"or": [{"switch_is_on": "a"}, {"switch_is_on": "b"}]}
    assert evaluate_formula(formula, {"a": False, "b": True}) is True
    assert evaluate_formula(formula, {"a": False, "b": False}) is False


def test_evaluate_nested() -> None:

    formula = {"and": [{"switch_is_on": "a"}, {"not": [{"switch_is_on": "b"}]}]}
    assert evaluate_formula(formula, {"a": True, "b": False}) is True
    assert evaluate_formula(formula, {"a": True, "b": True}) is False


def test_gate_with_and_formula() -> None:
    gate = arcade.Sprite()
    gate.texture = TEXTURE_GATE_CLOSED
    formula = {"and": [{"switch_is_on": "a"}, {"switch_is_on": "b"}]}
    gs, switches = _make_gate_system({"a": False, "b": False}, [(gate, formula)])

    gs.toggle_switch(switches["a"])
    gs.update()
    assert gate in gs.walls

    gs.toggle_switch(switches["b"])
    gs.update()
    assert gate not in gs.walls


def test_gate_with_not_formula() -> None:
    gate = arcade.Sprite()
    gate.texture = TEXTURE_GATE_CLOSED
    formula = {"not": [{"switch_is_on": "a"}]}
    gs, switches = _make_gate_system({"a": False}, [(gate, formula)])

    gs.update()
    assert gate not in gs.walls
