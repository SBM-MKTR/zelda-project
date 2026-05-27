from dataclasses import dataclass
import arcade
from constants import BAT_MOVEMENT_RADIUS, SCALE, SWITCH_SCALE, TILE_SIZE, BLOB_NAVMESH_SUBDIVISIONS
from enemies import BatEnemy, Enemy, SpinnerEnemy
from gate_system import GateInfo, SwitchInfo
from map import Map, bat_bounds, spinner_bounds
from map_types import GridCell, TeleporterConfig, KeyConfig, ChestConfig
from blob import BlobEnemy, build_possible_destinations
from navmesh import build_navmesh
from power_system import PowerSystem
from textures import (
    ANIMATION_BAT,
    ANIMATION_CRYSTAL,
    ANIMATION_SPINNERS,
    TEXTURE_BUSH,
    TEXTURE_GATE_CLOSED,
    TEXTURE_GRASS,
    TEXTURE_HOLE,
    TEXTURE_SWITCH_OFF,
    TEXTURE_SWITCH_ON,
    TEXTURE_TELEPORTER,
    TEXTURE_ICE,
    ANIMATION_BLOB,
    ANIMATION_KEY,
    ANIMATION_CHEST,
)

TeleporterInfo = tuple[arcade.Sprite, TeleporterConfig]
KeyInfo = tuple[arcade.TextureAnimationSprite, KeyConfig]
ChestInfo = tuple[arcade.TextureAnimationSprite, ChestConfig]

@dataclass
class Level:
    world_width: int
    world_height: int
    grounds: arcade.SpriteList[arcade.Sprite]
    walls: arcade.SpriteList[arcade.Sprite]
    ices: arcade.SpriteList[arcade.Sprite]
    crystals: arcade.SpriteList[arcade.TextureAnimationSprite]
    spinners: arcade.SpriteList[arcade.TextureAnimationSprite]
    holes: arcade.SpriteList[arcade.Sprite]
    bats: arcade.SpriteList[arcade.TextureAnimationSprite]
    switches: arcade.SpriteList[arcade.Sprite]
    gates: arcade.SpriteList[arcade.Sprite]
    teleporters: arcade.SpriteList[arcade.Sprite]
    keys: arcade.SpriteList[arcade.TextureAnimationSprite]
    chests: arcade.SpriteList[arcade.TextureAnimationSprite]
    enemies: list[Enemy]
    switch_infos: list[SwitchInfo]
    gate_infos: list[GateInfo]
    teleporter_infos: list[TeleporterInfo]
    blobs: arcade.SpriteList[arcade.TextureAnimationSprite]
    enemy_sprites: arcade.SpriteList[arcade.TextureAnimationSprite]
    key_infos: list[KeyInfo]
    chest_infos: list[ChestInfo]

    def remove_enemy_sprite(self, sprite: arcade.TextureAnimationSprite) -> None:
        self.enemies = [
            enemy
            for enemy in self.enemies
            if enemy.sprite is not sprite
        ]

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + TILE_SIZE // 2


def build_level(game_map: Map) -> Level:
    grounds: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    walls: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    ices: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    crystals: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=True)
    spinners: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=False)
    holes: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    bats: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=False)
    switches: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    gates: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    teleporters: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    keys: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=True)
    chests: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=True)
    enemies: list[Enemy] = []
    switch_infos: list[SwitchInfo] = []
    gate_infos: list[GateInfo] = []
    teleporter_infos: list[TeleporterInfo] = []
    key_infos: list[KeyInfo] = []
    chest_infos: list[ChestInfo] = []
    blobs: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=False)
    enemy_sprites: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=False)
    navmesh = build_navmesh(game_map, BLOB_NAVMESH_SUBDIVISIONS)

    switch_configs_by_position = {
        (switch.x, switch.y): switch
        for switch in game_map.switch_configs
    }
    gate_configs_by_position = {
        (gate.x, gate.y): gate
        for gate in game_map.gate_configs
    }
    teleporter_configs_by_position = {
        (tp.x, tp.y): tp
        for tp in game_map.teleporter_configs
    }
    key_configs_by_position = {
        (kc.x, kc.y): kc
        for kc in game_map.key_configs
    }
    chest_configs_by_position = {
        (cc.x, cc.y): cc
        for cc in game_map.chest_configs
    }

    for y in range(game_map.height):
        for x in range(game_map.width):
            center_x = grid_to_pixels(x)
            center_y = grid_to_pixels(y)

            grounds.append(
                arcade.Sprite(
                    TEXTURE_GRASS,
                    scale=SCALE,
                    center_x=center_x,
                    center_y=center_y,
                )
            )

            cell = game_map.get(x, y)

            match cell:
                case GridCell.GRASS:
                    pass

                case GridCell.BUSH:
                    walls.append(
                        arcade.Sprite(
                            TEXTURE_BUSH,
                            scale=SCALE,
                            center_x=center_x,
                            center_y=center_y,
                        )
                    )

                case GridCell.ICE:
                    ices.append(
                        arcade.Sprite(
                            TEXTURE_ICE,
                            scale=SCALE,
                            center_x=center_x,
                            center_y=center_y,
                        )
                    )

                case GridCell.CRYSTAL:
                    crystals.append(
                        arcade.TextureAnimationSprite(
                            animation=ANIMATION_CRYSTAL,
                            scale=SCALE,
                            center_x=center_x,
                            center_y=center_y,
                        )
                    )

                case GridCell.SPINNER_HORIZONTAL | GridCell.SPINNER_VERTICAL:
                    spinner = arcade.TextureAnimationSprite(
                        animation=ANIMATION_SPINNERS,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    bounds = spinner_bounds(game_map, x, y)
                    min_x_pixels = grid_to_pixels(bounds.min_x)
                    max_x_pixels = grid_to_pixels(bounds.max_x)
                    min_y_pixels = grid_to_pixels(bounds.min_y)
                    max_y_pixels = grid_to_pixels(bounds.max_y)

                    enemy: Enemy = SpinnerEnemy.from_bounds(
                        sprite=spinner,
                        min_x=min_x_pixels,
                        max_x=max_x_pixels,
                        min_y=min_y_pixels,
                        max_y=max_y_pixels,
                        is_horizontal=cell == GridCell.SPINNER_HORIZONTAL,
                    )

                    spinners.append(spinner)
                    enemies.append(enemy)
                    enemy_sprites.append(spinner)

                case GridCell.HOLE:
                    holes.append(
                        arcade.Sprite(
                            TEXTURE_HOLE,
                            scale=SCALE,
                            center_x=center_x,
                            center_y=center_y,
                        )
                    )

                case GridCell.BAT:
                    bat = arcade.TextureAnimationSprite(
                        animation=ANIMATION_BAT,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    enemy = BatEnemy(
                        sprite=bat,
                        bounds=bat_bounds(game_map, x, y, BAT_MOVEMENT_RADIUS),
                    )

                    bats.append(bat)
                    enemies.append(enemy)
                    enemy_sprites.append(bat)

                case GridCell.SWITCH:
                    switch_config = switch_configs_by_position[(x, y)]
                    texture = (
                        TEXTURE_SWITCH_ON
                        if switch_config.state
                        else TEXTURE_SWITCH_OFF
                    )

                    switch = arcade.Sprite(
                        texture,
                        scale=SWITCH_SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    switches.append(switch)
                    switch_infos.append((switch, switch_config.id))

                case GridCell.GATE:
                    gate_config = gate_configs_by_position[(x, y)]

                    gate = arcade.Sprite(
                        TEXTURE_GATE_CLOSED,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    walls.append(gate)
                    gate_infos.append((gate, gate_config))

                case GridCell.BLOB:
                    blob = arcade.TextureAnimationSprite(
                        animation=ANIMATION_BLOB,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    enemy = BlobEnemy(
                        sprite=blob,
                        navmesh=navmesh,
                        navmesh_subdivisions=BLOB_NAVMESH_SUBDIVISIONS,
                        possible_destinations=build_possible_destinations(game_map, x, y),
                    )

                    blobs.append(blob)
                    enemy_sprites.append(blob)
                    enemies.append(enemy)

                case GridCell.TELEPORTER:
                    tp_config = teleporter_configs_by_position[(x, y)]

                    tp_sprite = arcade.Sprite(
                        TEXTURE_TELEPORTER,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    teleporters.append(tp_sprite)
                    teleporter_infos.append((tp_sprite, tp_config))

                case GridCell.KEY:
                    key_config = key_configs_by_position[(x, y)]

                    key_sprite = arcade.TextureAnimationSprite(
                        animation=ANIMATION_KEY,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    keys.append(key_sprite)
                    key_infos.append((key_sprite, key_config))

                case GridCell.CHEST:
                    chest_config = chest_configs_by_position[(x, y)]

                    chest_sprite = arcade.TextureAnimationSprite(
                        animation=ANIMATION_CHEST,
                        scale=SCALE,
                        center_x=center_x,
                        center_y=center_y,
                    )

                    chests.append(chest_sprite)
                    chest_infos.append((chest_sprite, chest_config))

    return Level(
        world_width=game_map.width * TILE_SIZE,
        world_height=game_map.height * TILE_SIZE,
        grounds=grounds,
        walls=walls,
        ices=ices,
        crystals=crystals,
        spinners=spinners,
        holes=holes,
        bats=bats,
        switches=switches,
        gates=gates,
        teleporters=teleporters,
        keys=keys,
        chests=chests,
        enemies=enemies,
        switch_infos=switch_infos,
        gate_infos=gate_infos,
        teleporter_infos=teleporter_infos,
        key_infos=key_infos,
        chest_infos=chest_infos,
        blobs=blobs,
        enemy_sprites=enemy_sprites,
    )
