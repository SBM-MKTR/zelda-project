from dataclasses import dataclass
import arcade
from constants import BAT_MOVEMENT_RADIUS, SCALE, SWITCH_SCALE, TILE_SIZE
from enemies import BatEnemy, Enemy, SpinnerEnemy
from map import Map, bat_bounds, spinner_bounds
from map_types import GateConfig, GridCell
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
)

SwitchInfo = tuple[arcade.Sprite, str]
GateInfo = tuple[arcade.Sprite, GateConfig]


@dataclass
class Level:
    world_width: int
    world_height: int
    grounds: arcade.SpriteList[arcade.Sprite]
    walls: arcade.SpriteList[arcade.Sprite]
    crystals: arcade.SpriteList[arcade.TextureAnimationSprite]
    spinners: arcade.SpriteList[arcade.TextureAnimationSprite]
    holes: arcade.SpriteList[arcade.Sprite]
    bats: arcade.SpriteList[arcade.TextureAnimationSprite]
    switches: arcade.SpriteList[arcade.Sprite]
    gates: arcade.SpriteList[arcade.Sprite]
    enemies: list[Enemy]
    switch_infos: list[SwitchInfo]
    gate_infos: list[GateInfo]

    def remove_enemy_sprite(self, sprite: arcade.TextureAnimationSprite) -> None:
        self.enemies = [
            enemy
            for enemy in self.enemies
            if enemy.sprite is not sprite
        ]

def grid_to_pixels(i: int) -> int:
    return i * TILE_SIZE + TILE_SIZE // 2


def build_level(game_map: Map) -> Level:
    grounds: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=False)
    walls: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    crystals: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=True)
    spinners: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=False)
    holes: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=False)
    bats: arcade.SpriteList[arcade.TextureAnimationSprite] = arcade.SpriteList(use_spatial_hash=False)
    switches: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    gates: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=False)
    enemies: list[Enemy] = []
    switch_infos: list[SwitchInfo] = []
    gate_infos: list[GateInfo] = []

    switch_configs_by_position = {
        (switch.x, switch.y): switch
        for switch in game_map.switch_configs
    }
    gate_configs_by_position = {
        (gate.x, gate.y): gate
        for gate in game_map.gate_configs
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

                    enemy = SpinnerEnemy.from_bounds(
                        sprite=spinner,
                        min_x=min_x_pixels,
                        max_x=max_x_pixels,
                        min_y=min_y_pixels,
                        max_y=max_y_pixels,
                        is_horizontal=cell == GridCell.SPINNER_HORIZONTAL,
                    )

                    spinners.append(spinner)
                    enemies.append(enemy)

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
                    pass

    return Level(
        world_width=game_map.width * TILE_SIZE,
        world_height=game_map.height * TILE_SIZE,
        grounds=grounds,
        walls=walls,
        crystals=crystals,
        spinners=spinners,
        holes=holes,
        bats=bats,
        switches=switches,
        gates=gates,
        enemies=enemies,
        switch_infos=switch_infos,
        gate_infos=gate_infos,
    )
