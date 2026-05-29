from enum import Enum
import math

import arcade

from constants import BOOMERANG_MAX_DISTANCE, BOOMERANG_SPEED, SCALE
from player import Direction, Player
from textures import ANIMATION_BOOMERANG

class BoomerangState(Enum):
    INACTIVE = 0
    LAUNCHING = 1
    RETURNING = 2

class Boomerang(arcade.TextureAnimationSprite):
    """Sprite throwed by the player that travels in one direction
    then comes back to him."""

    def __init__(self) -> None:
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=SCALE,
        )

        self.state = BoomerangState.INACTIVE
        self.start_x = 0.0
        self.start_y = 0.0
        self.dir_x = 0.0
        self.dir_y = 0.0

    def launch(self, player: Player) -> None:
        if self.state != BoomerangState.INACTIVE:
            return

        self.center_x = player.center_x
        self.center_y = player.center_y

        self.start_x = self.center_x
        self.start_y = self.center_y

        match player.direction:
            case Direction.EAST:
                dx, dy = 1, 0
            case Direction.WEST:
                dx, dy = -1, 0
            case Direction.NORTH:
                dx, dy = 0, 1
            case Direction.SOUTH:
                dx, dy = 0, -1

        self.dir_x = dx
        self.dir_y = dy

        self.state = BoomerangState.LAUNCHING

    def update_boomerang(self, player: Player) -> None:
        """Advances the boomerang one frame: moves forward while LAUNCHING until max distance,
        then comes back to the player while RETURNING."""

        if self.state == BoomerangState.LAUNCHING:
            self.center_x += self.dir_x * BOOMERANG_SPEED
            self.center_y += self.dir_y * BOOMERANG_SPEED

            dx = self.center_x - self.start_x
            dy = self.center_y - self.start_y
            distance = math.hypot(dx, dy)
            if distance >= BOOMERANG_MAX_DISTANCE:
                self.state = BoomerangState.RETURNING

        elif self.state == BoomerangState.RETURNING:
            dx = player.center_x - self.center_x
            dy = player.center_y - self.center_y

            dist = math.hypot(dx, dy)

            if dist <= BOOMERANG_SPEED:
                # Directly stop the boomerang if it's close enough to be caught during the next update,
                # instead of setting a pre-defined fixed distance
                self.state = BoomerangState.INACTIVE
                self.center_x = player.center_x
                self.center_y = player.center_y
                return

            # Normalize the boomerang -> player vector (to use it as a direction vector)
            # This way the boomerang moves at the same speed regardless of its distance from the playe
            dx /= dist
            dy /= dist

            self.center_x += dx * BOOMERANG_SPEED
            self.center_y += dy * BOOMERANG_SPEED
