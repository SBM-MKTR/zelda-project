from abc import ABC, abstractmethod
from typing import Final, TypeVar

import arcade

from boomerang import Boomerang, BoomerangState
from player import Player


SpriteT = TypeVar("SpriteT", bound=arcade.Sprite)


class Weapon(ABC):
    @abstractmethod
    def update(self, player: Player) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    def check_target_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        pass

    @abstractmethod
    def check_obstacle_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        pass

    @abstractmethod
    def on_hit(self) -> None:
        pass


class BoomerangWeapon(Weapon):
    boomerang: Final[Boomerang]
    sprites: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    def __init__(self) -> None:
        self.boomerang = Boomerang()
        self.sprites = arcade.SpriteList(use_spatial_hash=False)
        self.sprites.append(self.boomerang)

    def launch(self, player: Player) -> None:
        self.boomerang.launch(player)

    def update(self, player: Player) -> None:
        self.boomerang.update_boomerang(player)
        self.boomerang.update_animation()

    def draw(self) -> None:
        if self.is_active():
            self.sprites.draw()

    def is_active(self) -> bool:
        return self.boomerang.state != BoomerangState.INACTIVE

    def is_launching(self) -> bool:
        return self.boomerang.state == BoomerangState.LAUNCHING

    def check_target_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        if not self.is_active():
            return []

        return arcade.check_for_collision_with_list(self.boomerang, sprite_list)

    def check_obstacle_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[SpriteT]:
        if not self.is_launching():
            return []

        return arcade.check_for_collision_with_list(self.boomerang, sprite_list)

    def on_hit(self) -> None:
        if self.is_launching():
            self.boomerang.state = BoomerangState.RETURNING


class WeaponSystem:
    boomerang_weapon: Final[BoomerangWeapon]
    weapons: Final[tuple[Weapon, ...]]
    boomerang: Final[Boomerang]
    boomerangs: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]

    def __init__(self) -> None:
        self.boomerang_weapon = BoomerangWeapon()
        self.weapons = (self.boomerang_weapon,)

        self.boomerang = self.boomerang_weapon.boomerang
        self.boomerangs = self.boomerang_weapon.sprites

    def launch_boomerang(self, player: Player) -> None:
        self.boomerang_weapon.launch(player)

    def update(self, player: Player) -> None:
        for weapon in self.weapons:
            weapon.update(player)

    def draw(self) -> None:
        for weapon in self.weapons:
            weapon.draw()

    def check_target_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[tuple[Weapon, SpriteT]]:
        collisions: list[tuple[Weapon, SpriteT]] = []

        for weapon in self.weapons:
            for sprite in weapon.check_target_collisions(sprite_list):
                collisions.append((weapon, sprite))

        return collisions

    def check_obstacle_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[tuple[Weapon, SpriteT]]:
        collisions: list[tuple[Weapon, SpriteT]] = []

        for weapon in self.weapons:
            for sprite in weapon.check_obstacle_collisions(sprite_list):
                collisions.append((weapon, sprite))

        return collisions
