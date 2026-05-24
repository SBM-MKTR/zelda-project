
from typing import Final
from enum import Enum, auto
from textures import *
from constants import *
import arcade



class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()

class Player(arcade.TextureAnimationSprite) :
    direction : Direction
    __right_pressed : bool
    __down_pressed : bool
    __left_pressed : bool
    __up_pressed : bool

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

    def press_direction(self, direction: Direction) -> None:
        self.__set_direction_update(direction, True)
        self.__update_direction_and_animation()
        self.__update_velocity()

    def release_direction(self, direction: Direction) -> None:
        self.__set_direction_update(direction, False)
        self.__update_direction_and_animation()
        self.__update_velocity()

    def __set_direction_update(self, direction : Direction, is_pressed : bool) -> None :
        match direction :
            case Direction.EAST:
                self.__right_pressed = is_pressed
            case Direction.WEST:
                self.__left_pressed = is_pressed
            case Direction.NORTH:
                self.__up_pressed = is_pressed
            case Direction.SOUTH:
                self.__down_pressed = is_pressed

    def __update_velocity(self) -> None:
        if self.__right_pressed and not self.__left_pressed :
            self.change_x = PLAYER_MOVEMENT_SPEED
        elif self.__left_pressed and not self.__right_pressed :
            self.change_x = - PLAYER_MOVEMENT_SPEED
        else :
            self.change_x = 0

        if self.__up_pressed and not self.__down_pressed:
            self.change_y = PLAYER_MOVEMENT_SPEED
        elif self.__down_pressed and not self.__up_pressed:
            self.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            self.change_y = 0

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
