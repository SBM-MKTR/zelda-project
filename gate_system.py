from dataclasses import dataclass, field

import arcade

from map_parser import evaluate_formula
from map_types import GateConfig
from textures import (
    TEXTURE_GATE_CLOSED,
    TEXTURE_GATE_OPEN,
    TEXTURE_SWITCH_OFF,
    TEXTURE_SWITCH_ON,
)


SwitchInfo = tuple[arcade.Sprite, str]
GateInfo = tuple[arcade.Sprite, GateConfig]


@dataclass
class GateSystem:
    switch_infos: list[SwitchInfo]
    gate_infos: list[GateInfo]
    walls: arcade.SpriteList[arcade.Sprite]
    gates: arcade.SpriteList[arcade.Sprite]
    _switch_state_map: dict[arcade.Sprite, bool] = field(
        init=False, default_factory=dict
    )

    def __post_init__(self) -> None:
        # Initialise l'état logique depuis la texture initiale (définie dans level.py).
        # Après cela, la texture est une conséquence de l'état, non plus sa source.
        self._switch_state_map = {
            sprite: sprite.texture == TEXTURE_SWITCH_ON
            for sprite, _ in self.switch_infos
        }

    def update(self) -> None:
        switch_states = self._switch_states()

        for gate_sprite, gate_config in self.gate_infos:
            is_open = evaluate_formula(gate_config.open_if, switch_states)
            self._set_gate_open(gate_sprite, is_open)

    def toggle_switch(self, switch: arcade.Sprite) -> None:
        if switch not in self._switch_state_map:
            raise ValueError("switch sprite inconnu")
        new_state = not self._switch_state_map[switch]
        self._switch_state_map[switch] = new_state
        switch.texture = TEXTURE_SWITCH_ON if new_state else TEXTURE_SWITCH_OFF

    def _switch_states(self) -> dict[str, bool]:
        return {
            switch_id: self._switch_state_map[sprite]
            for sprite, switch_id in self.switch_infos
        }

    def _set_gate_open(self, gate: arcade.Sprite, is_open: bool) -> None:
        if is_open:
            gate.texture = TEXTURE_GATE_OPEN

            if gate in self.walls:
                gate.remove_from_sprite_lists()

            if gate not in self.gates:
                self.gates.append(gate)

        else:
            gate.texture = TEXTURE_GATE_CLOSED

            if gate in self.gates:
                gate.remove_from_sprite_lists()

            if gate not in self.walls:
                self.walls.append(gate)
