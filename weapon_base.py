from abc import ABC, abstractmethod
from typing import TypeVar

import arcade

from player import Player

SpriteT = TypeVar("SpriteT", bound=arcade.Sprite)

class Weapon(ABC):
    @abstractmethod
    def use(self, player: Player) -> None:
        pass

    @abstractmethod
    def update(self, player: Player, delta_time: float) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def is_active(self) -> bool:
        pass

    @abstractmethod
    def check_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        pass

    @abstractmethod
    def on_hit(self) -> None:
        pass

    def can_hit_enemies(self) -> bool:
        return True

    def can_toggle_switches(self) -> bool:
        return False

    def can_collect_crystals(self) -> bool:
        return False

    def can_hit_obstacles(self) -> bool:
        return False
