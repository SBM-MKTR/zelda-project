
from typing import Final
from enum import Enum, auto
from constants import GROUND_FRICTION, ICE_FRICTION, ICE_MAX_SPEED, PLAYER_MOVEMENT_SPEED, SCALE
from textures import (
    ANIMATION_PLAYER_IDLE_DOWN,
    ANIMATION_PLAYER_IDLE_LEFT,
    ANIMATION_PLAYER_IDLE_RIGHT,
    ANIMATION_PLAYER_IDLE_UP,
)
import arcade



class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()

class Player(arcade.TextureAnimationSprite) :
    """The player character. Handles directions,
    velocity with optional ice physics, and facing animation."""
    direction : Direction
    __right_pressed : bool
    __down_pressed : bool
    __left_pressed : bool
    __up_pressed : bool
    __vel_x: float
    __vel_y: float

    def __init__(self, center_x : int, center_y : int) -> None :
        super().__init__(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE,
            center_x=center_x,
            center_y=center_y,
        )


        self.direction = Direction.SOUTH
        self.__right_pressed = False
        self.__left_pressed = False
        self.__up_pressed = False
        self.__down_pressed = False
        self.__vel_x = 0.0
        self.__vel_y = 0.0

    def press_direction(self, direction: Direction) -> None:
        self.__set_direction_pressed(direction, True)
        self.__update_direction_and_animation()

    def release_direction(self, direction: Direction) -> None:
        self.__set_direction_pressed(direction, False)
        self.__update_direction_and_animation()

    def update_physics(self, on_ice: bool) -> None:
        """
        Changes the current velocity into the target velocity.
        On ice: slow acceleration and very low friction (high inertia).
        On ground: instant response (friction = 1.0).
        """
        friction = ICE_FRICTION if on_ice else GROUND_FRICTION
        max_speed = ICE_MAX_SPEED if on_ice else PLAYER_MOVEMENT_SPEED

        target_x, target_y = self.__target_velocity(max_speed)

        self.__vel_x += (target_x - self.__vel_x) * friction
        self.__vel_y += (target_y - self.__vel_y) * friction

        # Set to zero to avoid drifting forever
        if abs(self.__vel_x) < 0.01:
            self.__vel_x = 0.0
        if abs(self.__vel_y) < 0.01:
            self.__vel_y = 0.0

        self.change_x = self.__vel_x
        self.change_y = self.__vel_y

    def __target_velocity(self, max_speed: float) -> tuple[float, float]:
        """Returns the velocity the player is trying to reach based on pressed keys."""
        target_x = 0.0
        target_y = 0.0

        if self.__right_pressed and not self.__left_pressed:
            target_x = max_speed
        elif self.__left_pressed and not self.__right_pressed:
            target_x = -max_speed

        if self.__up_pressed and not self.__down_pressed:
            target_y = max_speed
        elif self.__down_pressed and not self.__up_pressed:
            target_y = -max_speed

        return target_x, target_y

    def __set_direction_pressed(self, direction : Direction, is_pressed : bool) -> None :
        match direction :
            case Direction.EAST:
                self.__right_pressed = is_pressed
            case Direction.WEST:
                self.__left_pressed = is_pressed
            case Direction.NORTH:
                self.__up_pressed = is_pressed
            case Direction.SOUTH:
                self.__down_pressed = is_pressed

    def __update_direction_and_animation(self) -> None:
        if self.__down_pressed:
            self.direction = Direction.SOUTH
            self.animation = ANIMATION_PLAYER_IDLE_DOWN
        elif self.__up_pressed:
            self.direction = Direction.NORTH
            self.animation = ANIMATION_PLAYER_IDLE_UP
        elif self.__left_pressed:
            self.direction = Direction.WEST
            self.animation = ANIMATION_PLAYER_IDLE_LEFT
        elif self.__right_pressed:
            self.direction = Direction.EAST
            self.animation = ANIMATION_PLAYER_IDLE_RIGHT
