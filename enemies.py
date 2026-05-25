from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import math
import random

import arcade

from constants import BAT_MOVEMENT_SPEED, SPINNER_MOVEMENT_SPEED
from map_types import BatBounds


class Enemy(ABC):
    sprite: arcade.TextureAnimationSprite

    @abstractmethod
    def update(self) -> None:
        pass


@dataclass
class SpinnerEnemy(Enemy):
    sprite: arcade.TextureAnimationSprite
    min_x: int
    max_x: int
    min_y: int
    max_y: int

    @classmethod
    def from_bounds(
        cls,
        sprite: arcade.TextureAnimationSprite,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
        is_horizontal: bool,
    ) -> "SpinnerEnemy":
        if is_horizontal and min_x != max_x:
            sprite.change_x = SPINNER_MOVEMENT_SPEED
        elif not is_horizontal and min_y != max_y:
            sprite.change_y = SPINNER_MOVEMENT_SPEED

        return cls(sprite, min_x, max_x, min_y, max_y)

    def update(self) -> None:
        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

        if self.sprite.change_x > 0 and self.sprite.center_x >= self.max_x:
            self.sprite.center_x = self.max_x
            self.sprite.change_x = -SPINNER_MOVEMENT_SPEED

        elif self.sprite.change_x < 0 and self.sprite.center_x <= self.min_x:
            self.sprite.center_x = self.min_x
            self.sprite.change_x = SPINNER_MOVEMENT_SPEED

        elif self.sprite.change_y > 0 and self.sprite.center_y >= self.max_y:
            self.sprite.center_y = self.max_y
            self.sprite.change_y = -SPINNER_MOVEMENT_SPEED

        elif self.sprite.change_y < 0 and self.sprite.center_y <= self.min_y:
            self.sprite.center_y = self.min_y
            self.sprite.change_y = SPINNER_MOVEMENT_SPEED


@dataclass
class BatEnemy(Enemy):
    sprite: arcade.TextureAnimationSprite
    bounds: BatBounds
    rng: random.Random = field(default_factory=random.Random)
    frame_count: int = 0

    def __post_init__(self) -> None:
        self._choose_random_direction()

    def update(self) -> None:
        self.frame_count += 1

        if self.frame_count % 50 == 0:
            angle = math.atan2(self.sprite.change_y, self.sprite.change_x)
            new_angle = self.rng.triangular(angle - math.pi, angle + math.pi, angle)
            self._set_direction(new_angle)

        self.sprite.center_x += self.sprite.change_x
        self.sprite.center_y += self.sprite.change_y

        if (
            self.sprite.center_x < self.bounds.center_x - self.bounds.radius
            or self.sprite.center_x > self.bounds.center_x + self.bounds.radius
        ):
            self.sprite.change_x *= -1

        if (
            self.sprite.center_y < self.bounds.center_y - self.bounds.radius
            or self.sprite.center_y > self.bounds.center_y + self.bounds.radius
        ):
            self.sprite.change_y *= -1

    def _choose_random_direction(self) -> None:
        self._set_direction(self.rng.uniform(0, 2 * math.pi))

    def _set_direction(self, angle: float) -> None:
        self.sprite.change_x = math.cos(angle) * BAT_MOVEMENT_SPEED
        self.sprite.change_y = math.sin(angle) * BAT_MOVEMENT_SPEED
