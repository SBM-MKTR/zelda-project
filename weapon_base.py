from abc import ABC, abstractmethod
from typing import TypeVar

import arcade

from player import Player

SpriteT = TypeVar("SpriteT", bound=arcade.Sprite)

def collect_new_collisions(
    collider: arcade.Sprite,
    sprite_list: arcade.SpriteList[SpriteT],
    hit_sprite_ids: set[int],
) -> list[SpriteT]:
    new_collisions: list[SpriteT] = []

    for sprite in arcade.check_for_collision_with_list(collider, sprite_list):
        sprite_id = id(sprite)

        if sprite_id in hit_sprite_ids:
            continue

        hit_sprite_ids.add(sprite_id)
        new_collisions.append(sprite)

    return new_collisions

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
