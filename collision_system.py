from dataclasses import dataclass

import arcade

from constants import HOLE_DEATH_RADIUS
from gate_system import GateSystem
from level import Level, TeleporterInfo
from player import Player
from weapon_base import Weapon
from weapon_system import WeaponSystem


@dataclass(frozen=True)
class CollisionResult:
    should_restart: bool = False
    score_delta: int = 0
    teleport_destination: tuple[float, float] | None = None


@dataclass
class CollisionSystem:
    level: Level
    player: Player
    weapon_system: WeaponSystem
    gate_system: GateSystem
    crystals_sound: arcade.Sound
    _teleport_cooldown: int = 0

    def update(self) -> CollisionResult:
        if self._player_falls_in_hole():
            return CollisionResult(should_restart=True)

        score_delta = self._collect_player_crystals()
        score_delta += self._collect_weapon_crystals()

        self._handle_weapon_enemy_hits()
        self._handle_weapon_switch_hits()
        self._handle_weapon_obstacle_hits()

        if self._player_touches_enemy():
            return CollisionResult(should_restart=True, score_delta=score_delta)

        if self._teleport_cooldown > 0:
            self._teleport_cooldown -= 1

        teleport_dest = self._check_teleportation()
        if teleport_dest is not None:
            return CollisionResult(score_delta=score_delta, teleport_destination=teleport_dest)

        return CollisionResult(score_delta=score_delta)

    def _player_touches_enemy(self) -> bool:
        return bool(
            arcade.check_for_collision_with_list(self.player, self.level.spinners)
            or arcade.check_for_collision_with_list(self.player, self.level.bats)
        )

    def _player_falls_in_hole(self) -> bool:
        radius_squared = HOLE_DEATH_RADIUS * HOLE_DEATH_RADIUS

        for hole in self.level.holes:
            dx = self.player.center_x - hole.center_x
            dy = self.player.center_y - hole.center_y

            if dx * dx + dy * dy <= radius_squared:
                return True

        return False

    def _collect_player_crystals(self) -> int:
        score_delta = 0

        for crystal in arcade.check_for_collision_with_list(
            self.player,
            self.level.crystals,
        ):
            self._collect_crystal(crystal)
            score_delta += 1

        return score_delta

    def _collect_weapon_crystals(self) -> int:
        score_delta = 0

        for _weapon, crystal in self.weapon_system.check_crystal_collisions(
            self.level.crystals,
        ):
            self._collect_crystal(crystal)
            score_delta += 1

        return score_delta

    def _collect_crystal(self, crystal: arcade.TextureAnimationSprite) -> None:
        crystal.remove_from_sprite_lists()
        arcade.play_sound(self.crystals_sound)

    def _handle_weapon_enemy_hits(self) -> None:
        for weapon, spinner in self.weapon_system.check_enemy_collisions(
            self.level.spinners,
        ):
            self._remove_enemy_hit(spinner, weapon)

        for weapon, bat in self.weapon_system.check_enemy_collisions(
            self.level.bats,
        ):
            self._remove_enemy_hit(bat, weapon)

    def _remove_enemy_hit(
        self,
        enemy_sprite: arcade.TextureAnimationSprite,
        weapon: Weapon,
    ) -> None:
        self.level.remove_enemy_sprite(enemy_sprite)
        enemy_sprite.remove_from_sprite_lists()
        weapon.on_hit()

    def _handle_weapon_switch_hits(self) -> None:
        for weapon, switch in self.weapon_system.check_switch_collisions(
            self.level.switches,
        ):
            self.gate_system.toggle_switch(switch)
            weapon.on_hit()

    def _handle_weapon_obstacle_hits(self) -> None:
        for weapon, _wall in self.weapon_system.check_obstacle_collisions(
            self.level.walls,
        ):
            weapon.on_hit()

    def _check_teleportation(self) -> tuple[float, float] | None:
        """Returns the pixel destination if the player steps on a teleporter, else None."""
        if self._teleport_cooldown > 0:
            return None

        for tp_sprite, tp_config in self.level.teleporter_infos:
            if not arcade.check_for_collision(self.player, tp_sprite):
                continue

            target_sprite: arcade.Sprite | None = None
            for other_sprite, other_config in self.level.teleporter_infos:
                if other_config.id == tp_config.target_id:
                    target_sprite = other_sprite
                    break

            if target_sprite is None:
                continue

            self._teleport_cooldown = 60
            return (target_sprite.center_x, target_sprite.center_y)

        return None
