from dataclasses import dataclass, field
import arcade
from constants import HOLE_DEATH_RADIUS
from gate_system import GateSystem
from level import Level
from player import Player
from weapon_base import Weapon
from weapon_system import WeaponSystem
from textures import ANIMATION_CHEST_OPEN, ANIMATION_CHEST_STAYS_OPEN
from power_system import PowerSystem


@dataclass(frozen=True)
class CollisionResult:
    """Immutable result of one CollisionSystem.update() tick:
    death flag, score delta, teleport destination, chest message."""
    should_restart: bool = False
    score_delta: int = 0
    teleport_destination: tuple[float, float] | None = None
    chest_message: str | None = None


@dataclass
class CollisionSystem:
    """Centralises all collision checks
    and returns a CollisionResult instead of changing state directly."""
    level: Level
    player: Player
    weapon_system: WeaponSystem
    gate_system: GateSystem
    crystals_sound: arcade.Sound
    power_system: PowerSystem
    _teleport_cooldown: int = 0
    _collected_key_ids: set[str] = field(default_factory=set, init=False)
    _opening_chests: set[arcade.TextureAnimationSprite] = field(default_factory=set, init=False)

    def update(self) -> CollisionResult:
        """Runs all collision checks for one frame and
        returns a CollisionResult telling what happened
        (death, score, teleport, chest message)."""
        if self._player_falls_in_hole():
            return CollisionResult(should_restart=True)

        score_delta = self._collect_player_crystals()
        score_delta += self._collect_weapon_crystals()

        self._handle_weapon_enemy_hits()
        self._handle_weapon_switch_hits()
        self._handle_weapon_obstacle_hits()
        self._handle_key_pickups()
        self._update_opening_chests()

        if self._player_touches_enemy() and (not self.power_system.is_ghost_active and not self.power_system.is_frozen_active):
            return CollisionResult(should_restart=True, score_delta=score_delta)

        if self._teleport_cooldown > 0:
            self._teleport_cooldown -= 1

        teleport_dest = self._check_teleportation()
        if teleport_dest is not None:
            return CollisionResult(score_delta=score_delta, teleport_destination=teleport_dest)

        chest_message = self._handle_chest_openings()

        return CollisionResult(score_delta=score_delta, chest_message=chest_message)

    def _player_touches_enemy(self) -> bool:
        return bool(
            arcade.check_for_collision_with_list(
                self.player,
                self.level.enemy_sprites,
            )
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
        for weapon, enemy in self.weapon_system.check_enemy_collisions(self.level.enemy_sprites):
            self._remove_enemy_hit(enemy, weapon)

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

    def _handle_key_pickups(self) -> None:
        for key_sprite, key_config in list(self.level.key_infos):
            if not arcade.check_for_collision(self.player, key_sprite):
                continue

            self._collected_key_ids.add(key_config.id)
            key_sprite.remove_from_sprite_lists()
            self.level.key_infos.remove((key_sprite, key_config))

    def _handle_chest_openings(self) -> str | None:
        """Opens a chest if the player stands on it and holds the matching key.
        Returns a message string if access is denied, else None."""
        for chest_sprite, chest_config in list(self.level.chest_infos):
            if not arcade.check_for_collision(self.player, chest_sprite):
                continue

            if not self._collected_key_ids:
                return "You need a key to open this chest !"

            if chest_config.key_id not in self._collected_key_ids:
                return "Wrong key for this chest !"

            chest_sprite.animation = ANIMATION_CHEST_OPEN
            self._opening_chests.add(chest_sprite)
            self.level.chest_infos.remove((chest_sprite, chest_config))
            self._collected_key_ids.discard(chest_config.key_id)
            self.power_system.activate_random_power()

        return None

    def _update_opening_chests(self) -> None:
        """Handles the animation part of chests"""
        for chest_sprite in list(self._opening_chests):
            frames = len(ANIMATION_CHEST_OPEN.keyframes)
            duration = ANIMATION_CHEST_OPEN.keyframes[0].duration  # ms per frame
            total_ms = frames * duration
            if chest_sprite.time * 1000 >= total_ms:
                chest_sprite.animation = ANIMATION_CHEST_STAYS_OPEN
                self._opening_chests.discard(chest_sprite)

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

            self._teleport_cooldown = 60 # 1-second cooldown to avoid immediately teleporting back
            return (target_sprite.center_x, target_sprite.center_y)

        return None
