from enum import Enum, auto
from typing import Callable, Final
import arcade
from boomerang import Boomerang, BoomerangState
from constants import WEAPON_ICON_SCALE, WEAPON_ICON_TOP_MARGIN, WEAPON_ICON_X
from player import Player
from sword import SwordWeapon
from textures import ANIMATION_BOOMERANG, ANIMATION_SWORD_DOWN
from weapon_base import SpriteT, Weapon, collect_new_collisions


class ActiveWeapon(Enum):
    BOOMERANG = auto()
    SWORD = auto()


class BoomerangWeapon(Weapon):
    """Weapon adapter that wraps a Boomerang.
    Tracks hits per throw to avoid double-counting."""
    boomerang: Final[Boomerang]
    sprites: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    hit_sprite_ids: set[int]

    def __init__(self) -> None:
        self.boomerang = Boomerang()
        self.sprites = arcade.SpriteList(use_spatial_hash=False)
        self.sprites.append(self.boomerang)
        self.hit_sprite_ids = set()

    def use(self, player: Player) -> None:
        if self.is_active():
            return

        self.hit_sprite_ids.clear()
        self.boomerang.launch(player)

    def update(self, player: Player, delta_time: float) -> None:
        self.boomerang.update_boomerang(player)
        self.boomerang.update_animation(delta_time)

    def draw(self) -> None:
        if self.is_active():
            self.sprites.draw()

    def is_active(self) -> bool:
        return self.boomerang.state != BoomerangState.INACTIVE

    def is_launching(self) -> bool:
        return self.boomerang.state == BoomerangState.LAUNCHING

    def check_collisions(self, sprite_list: arcade.SpriteList[SpriteT]) -> list[SpriteT]:
        if not self.is_active():
            return []

        return collect_new_collisions(
            self.boomerang,
            sprite_list,
            self.hit_sprite_ids,
        )

    def on_hit(self) -> None:
        if self.is_launching():
            self.boomerang.state = BoomerangState.RETURNING

    def can_toggle_switches(self) -> bool:
        return True

    def can_hit_obstacles(self) -> bool:
        return self.is_launching()


class WeaponSystem:
    """Manages the two weapons (boomerang and sword),
    tracks the active one, and guides collision queries."""
    boomerang_weapon: Final[BoomerangWeapon]
    sword_weapon: Final[SwordWeapon]
    weapons: Final[tuple[Weapon, ...]]
    active_weapon: ActiveWeapon
    active_weapon_icon: Final[arcade.Sprite]

    def __init__(self) -> None:
        self.boomerang_weapon = BoomerangWeapon()
        self.sword_weapon = SwordWeapon()
        self.weapons = (self.boomerang_weapon, self.sword_weapon)
        self.active_weapon = ActiveWeapon.BOOMERANG

        self.active_weapon_icon = arcade.Sprite(
            self._active_weapon_icon_texture(),
            scale=WEAPON_ICON_SCALE,
        )

    def switch_active_weapon(self) -> None:
        if self.has_active_weapon():
            return

        if self.active_weapon == ActiveWeapon.BOOMERANG:
            self.active_weapon = ActiveWeapon.SWORD
        else:
            self.active_weapon = ActiveWeapon.BOOMERANG

    def use_active_weapon(self, player: Player) -> None:
        self._active_weapon().use(player)

    def launch_boomerang(self, player: Player) -> None:
        self.boomerang_weapon.use(player)

    def update(self, player: Player, delta_time: float) -> None:
        for weapon in self.weapons:
            weapon.update(player, delta_time)

    def draw(self) -> None:
        for weapon in self.weapons:
            weapon.draw()

    def draw_active_weapon_icon(self, window_height: int) -> None:
        self.active_weapon_icon.texture = self._active_weapon_icon_texture()
        self.active_weapon_icon.center_x = WEAPON_ICON_X
        self.active_weapon_icon.center_y = window_height - WEAPON_ICON_TOP_MARGIN
        arcade.draw_sprite(self.active_weapon_icon)

    def has_active_weapon(self) -> bool:
        return any(weapon.is_active() for weapon in self.weapons)

    def check_enemy_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[tuple[Weapon, SpriteT]]:
        return self._check_collisions(sprite_list, lambda weapon: weapon.can_hit_enemies())

    def check_switch_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[tuple[Weapon, SpriteT]]:
        return self._check_collisions(
            sprite_list,
            lambda weapon: weapon.can_toggle_switches(),
        )

    def check_crystal_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[tuple[Weapon, SpriteT]]:
        return self._check_collisions(
            sprite_list,
            lambda weapon: weapon.can_collect_crystals(),
        )

    def check_obstacle_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
    ) -> list[tuple[Weapon, SpriteT]]:
        return self._check_collisions(
            sprite_list,
            lambda weapon: weapon.can_hit_obstacles(),
        )

    def _check_collisions(
        self,
        sprite_list: arcade.SpriteList[SpriteT],
        predicate: Callable[[Weapon], bool],
    ) -> list[tuple[Weapon, SpriteT]]:
        collisions: list[tuple[Weapon, SpriteT]] = []

        for weapon in self.weapons:
            if not predicate(weapon):
                continue

            for sprite in weapon.check_collisions(sprite_list):
                collisions.append((weapon, sprite))

        return collisions

    def _active_weapon(self) -> Weapon:
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            return self.boomerang_weapon

        return self.sword_weapon

    def _active_weapon_icon_texture(self) -> arcade.Texture:
        if self.active_weapon == ActiveWeapon.BOOMERANG:
            return ANIMATION_BOOMERANG.keyframes[0].texture

        return ANIMATION_SWORD_DOWN.keyframes[0].texture
