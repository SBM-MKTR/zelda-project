from typing import Final, TypeVar

import arcade

from boomerang import Boomerang, BoomerangState
from player import Player


SpriteT = TypeVar("SpriteT", bound=arcade.Sprite)


class WeaponSystem:
    boomerang: Final[Boomerang]
    boomerangs: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    def __init__(self) -> None:
        self.boomerang = Boomerang()
        self.boomerangs = arcade.SpriteList(use_spatial_hash=False)
        self.boomerangs.append(self.boomerang)

    def launch_boomerang(self, player: Player) -> None:
        self.boomerang.launch(player)

    def update(self, player: Player) -> None:
        self.boomerang.update_boomerang(player)
        self.boomerang.update_animation()

    def draw(self) -> None:
        if self.is_boomerang_active():
            self.boomerangs.draw()

    def is_boomerang_active(self) -> bool:
        return self.boomerang.state != BoomerangState.INACTIVE

    def is_boomerang_launching(self) -> bool:
        return self.boomerang.state == BoomerangState.LAUNCHING

    def return_boomerang_if_launching(self) -> None:
        if self.is_boomerang_launching():
            self.boomerang.state = BoomerangState.RETURNING

    def check_boomerang_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        if not self.is_boomerang_active():
            return []

        return arcade.check_for_collision_with_list(self.boomerang, sprite_list)
