from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import math
import random

import arcade

from constants import BAT_MOVEMENT_SPEED, SPINNER_MOVEMENT_SPEED
from map_types import BatBounds
from player import Player


@dataclass(frozen=True)
class EnemyUpdateContext:
    """Current world state passed to each Enemy.update() call (read-only)."""
    player: Player
    line_of_sight_walls: arcade.SpriteList[arcade.Sprite]
    is_ghost_active: bool = False


class Enemy(ABC):
    """Abstract base for all enemies.
    Subclasses implement update() to define movement behaviour."""
    sprite: arcade.TextureAnimationSprite

    @abstractmethod
    def update(self, context: EnemyUpdateContext) -> None:
        """Advances the enemy by one frame.
        Must move the enemy's sprite without modifying context.
        Called every frame by GameView only when the freeze power is not active."""
        pass

@dataclass
class SpinnerEnemy(Enemy):
    """An enemy that goes in a straight line and bounces back and forth off walls."""
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

    def update(self, context: EnemyUpdateContext) -> None:
        """Moves the spinner on its straight line and reverses direction when hitting a boundary."""
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
    """An enemy that goes around randomly within a circular zone,
    slightly changing direction every few frames."""
    sprite: arcade.TextureAnimationSprite
    bounds: BatBounds
    rng: random.Random = field(default_factory=random.Random)
    frame_count: int = 0

    def __post_init__(self) -> None:
        self._choose_random_direction()

    def update(self, context: EnemyUpdateContext) -> None:
        """Moves the bat randomly within its bounding circle,
        changing direction every 50 frames."""
        self.frame_count += 1

        if self.frame_count % 50 == 0: # Change direction every 50 frames (approximetaly 0.8s since we have 60 fps)
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
