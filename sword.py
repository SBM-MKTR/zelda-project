from typing import Final

import arcade

from constants import (
    SCALE,
    SWORD_ATTACK_DURATION,
    SWORD_HITBOX_OFFSET,
    SWORD_HITBOX_SIZE,
)
from player import Direction, Player
from textures import (
    ANIMATION_SWORD_DOWN,
    ANIMATION_SWORD_LEFT,
    ANIMATION_SWORD_RIGHT,
    ANIMATION_SWORD_UP,
)
from weapon_base import SpriteT, Weapon, collect_new_collisions


class SwordWeapon(Weapon):
    sprite: Final[arcade.TextureAnimationSprite]
    hitbox: Final[arcade.Sprite]
    elapsed_time: float
    active: bool
    hit_sprite_ids: set[int]

    def __init__(self) -> None:
        self.sprite = arcade.TextureAnimationSprite(
            animation=ANIMATION_SWORD_DOWN,
            scale=SCALE,
        )
        self.hitbox = arcade.SpriteSolidColor(
            SWORD_HITBOX_SIZE,
            SWORD_HITBOX_SIZE,
        )
        self.elapsed_time = 0.0
        self.active = False
        self.hit_sprite_ids = set()

    def use(self, player: Player) -> None:
        if self.active:
            return

        animation = self._animation_for_direction(player.direction)

        self.sprite.animation = animation
        self.sprite.texture = animation.keyframes[0].texture
        self.sprite.time = 0.0
        self.sprite.center_x = player.center_x
        self.sprite.center_y = player.center_y

        self._place_hitbox(player)
        self.elapsed_time = 0.0
        self.hit_sprite_ids.clear()
        self.active = True

    def update(self, player: Player, delta_time: float) -> None:
        if not self.active:
            return

        self.elapsed_time += delta_time
        self.sprite.update_animation(delta_time)

        if self.elapsed_time >= SWORD_ATTACK_DURATION:
            self.active = False

    def draw(self) -> None:
        if self.active:
            arcade.draw_sprite(self.sprite)

    def is_active(self) -> bool:
        return self.active

    def check_collisions(self,sprite_list: arcade.SpriteList[SpriteT] ) -> list[SpriteT]:
        if not self.active:
            return []

        return collect_new_collisions(
            self.hitbox,
            sprite_list,
            self.hit_sprite_ids,
        )

    def on_hit(self) -> None:
        pass

    def can_toggle_switches(self) -> bool:
        return True

    def can_collect_crystals(self) -> bool:
        return True

    @staticmethod
    def _animation_for_direction(direction: Direction) -> arcade.TextureAnimation:
        match direction:
            case Direction.NORTH:
                return ANIMATION_SWORD_UP
            case Direction.SOUTH:
                return ANIMATION_SWORD_DOWN
            case Direction.WEST:
                return ANIMATION_SWORD_LEFT
            case Direction.EAST:
                return ANIMATION_SWORD_RIGHT

    def _place_hitbox(self, player: Player) -> None:
        self.hitbox.center_x = player.center_x
        self.hitbox.center_y = player.center_y

        match player.direction:
            case Direction.NORTH:
                self.hitbox.center_y += SWORD_HITBOX_OFFSET
            case Direction.SOUTH:
                self.hitbox.center_y -= SWORD_HITBOX_OFFSET
            case Direction.WEST:
                self.hitbox.center_x -= SWORD_HITBOX_OFFSET
            case Direction.EAST:
                self.hitbox.center_x += SWORD_HITBOX_OFFSET
