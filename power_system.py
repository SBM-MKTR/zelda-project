from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

import arcade

from player import Player
from enemies import Enemy
from constants import POWER_DURATION_FRAMES, GHOST_ALPHA




class Power(ABC):
    """Base class for all powers."""

    @abstractmethod
    def on_activate(self, player: Player, enemies: list[Enemy]) -> None:
        """Called once when the power is first applied."""

    @abstractmethod
    def on_deactivate(self, player: Player, enemies: list[Enemy]) -> None:
        """Called once when the power expires."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class GhostPower(Power):
    """Player becomes semi-transparent and invincible."""

    name = "Ghost"

    def on_activate(self, player: Player, enemies: list[Enemy]) -> None:
        player.alpha = GHOST_ALPHA

    def on_deactivate(self, player: Player, enemies: list[Enemy]) -> None:
        player.alpha = 255


class FreezePower(Power):
    """All enemies are frozen in place."""

    name = "Freeze"

    def on_activate(self, player: Player, enemies: list[Enemy]) -> None:
        pass

    def on_deactivate(self, player: Player, enemies: list[Enemy]) -> None:
        pass


ALL_POWERS: list[type[Power]] = [GhostPower, FreezePower]


@dataclass
class PowerSystem:
    player: Player
    enemies: list[Enemy]
    _active_power: Power | None = None
    _remaining_frames: int = 0

    def activate_random_power(self) -> None:
        """Picks a random power, deactivates any current one, and activates the new one."""
        if self._active_power is not None:
            self._active_power.on_deactivate(self.player, self.enemies)

        power_class = random.choice(ALL_POWERS)
        self._active_power = power_class()
        self._remaining_frames = POWER_DURATION_FRAMES
        self._active_power.on_activate(self.player, self.enemies)

    def update(self) -> None:
        """Must be called every frame. Counts down and deactivates expired powers."""
        if self._active_power is None:
            return

        self._remaining_frames -= 1

        if self._remaining_frames <= 0:
            self._active_power.on_deactivate(self.player, self.enemies)
            self._active_power = None

    @property
    def is_ghost_active(self) -> bool:
        return isinstance(self._active_power, GhostPower)

    @property
    def is_frozen_active(self) -> bool:
        return isinstance(self._active_power, FreezePower)

    @property
    def active_power_name(self) -> str | None:
        return self._active_power.name if self._active_power else None

    @property
    def remaining_frames(self) -> int:
        return self._remaining_frames
