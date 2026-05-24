from dataclasses import dataclass

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

    def update(self) -> None:
        switch_states = self._switch_states()

        for gate_sprite, gate_config in self.gate_infos:
            is_open = evaluate_formula(gate_config.open_if, switch_states)
            self._set_gate_open(gate_sprite, is_open)

    def toggle_switch(self, switch: arcade.Sprite) -> None:
        if switch.texture == TEXTURE_SWITCH_OFF:
            switch.texture = TEXTURE_SWITCH_ON
        elif switch.texture == TEXTURE_SWITCH_ON:
            switch.texture = TEXTURE_SWITCH_OFF
        else:
            raise ValueError("switch sprite has an unknown texture")

    def _switch_states(self) -> dict[str, bool]:
        return {
            switch_id: sprite.texture == TEXTURE_SWITCH_ON
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
