from enum import Enum
import arcade

from constants import *
from textures import *
from player import *



class BoomerangState(Enum):
    INACTIVE = 0
    LAUNCHING = 1
    RETURNING = 2

class Boomerang(arcade.TextureAnimationSprite):

    def __init__(self) -> None:
        super().__init__(
            animation=ANIMATION_BOOMERANG,
            scale=SCALE,
        )

        self.state = BoomerangState.INACTIVE
        self.start_x = 0
        self.start_y = 0
        self.dir_x = 0
        self.dir_y = 0

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

        if self.state == BoomerangState.LAUNCHING:
            self.center_x += self.dir_x * BOOMERANG_SPEED
            self.center_y += self.dir_y * BOOMERANG_SPEED

            dx = self.center_x - self.start_x
            dy = self.center_y - self.start_y
            distance = (dx**2 + dy**2)**0.5
            if distance >= BOOMERANG_MAX_DISTANCE:
                self.state = BoomerangState.RETURNING

        elif self.state == BoomerangState.RETURNING:
            dx = player.center_x - self.center_x
            dy = player.center_y - self.center_y

            dist = (dx**2 + dy**2)**0.5

            if dist <= BOOMERANG_SPEED:
                #si le boomerang est assez proche pour être rattrapé au prochain déplacement, on l’arrête directement
                # à la place de mettre un distance fixe préféfinie
                self.state = BoomerangState.INACTIVE
                self.center_x = player.center_x
                self.center_y = player.center_y
                return

            #on normalise le vecteur boomerang -> player (pour l'utiliser comme vecteur directeur)
            #comme ca le boomerang se deplace bien a la même vitesse quelque soit sa distance avec le player
            dx /= dist
            dy /= dist

            self.center_x += dx * BOOMERANG_SPEED
            self.center_y += dy * BOOMERANG_SPEED
