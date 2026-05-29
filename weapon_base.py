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
    """Abstract class for all weapons.
    Defines the contract for use, update, draw, and collision queries."""
    @abstractmethod
    def use(self, player: Player) -> None:
        """Activates the weapon from the player's current position and direction.
        Does nothing if already active."""
        pass

    @abstractmethod
    def update(self, player: Player, delta_time: float) -> None:
        """Advances the weapon's state by one frame.
        Called every frame regardless of whether the weapon is active.
        Implementations should move sprites, advance animations, and handle
        timed deactivation."""
        pass

    @abstractmethod
    def draw(self) -> None:
        """Draws the weapon's sprites. Does nothing when inactive."""
        pass

    @abstractmethod
    def is_active(self) -> bool:
        """Returns True if the weapon is currently in use.
        Used by WeaponSystem to block switching and to gate collision checks."""
        pass

    @abstractmethod
    def check_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        """Returns sprites from sprite_list that the weapon hit this frame.
        Must return [] when inactive."""
        pass

    @abstractmethod
    def on_hit(self) -> None:
        """Called when the weapon touches an enemy, switch, or obstacle.
        May change state (e.g. reverse boomerang)."""
        pass

    def can_hit_enemies(self) -> bool:
        return True

    def can_toggle_switches(self) -> bool:
        return False

    def can_collect_crystals(self) -> bool:
        return False

    def can_hit_obstacles(self) -> bool:
        return False
