import random

import arcade

from blob import BlobEnemy, build_possible_destinations
from constants import SCALE, TILE_SIZE
from enemies import EnemyUpdateContext
from gameview import GameView
from map import Map
from navmesh import build_navmesh
from player import Player
from textures import ANIMATION_BLOB


def center(x: int, y: int) -> tuple[int, int]:
    return (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2)


def make_blob_sprite(x: int, y: int) -> arcade.TextureAnimationSprite:
    return arcade.TextureAnimationSprite(
        animation=ANIMATION_BLOB,
        scale=SCALE,
        center_x=center(x, y)[0],
        center_y=center(x, y)[1],
    )


def test_blob_possible_destinations_exclude_obstacles_but_include_switches() -> None:
    game_map = Map.from_string("""width: 7
height: 5
switches:
  - id: sw1
    x: 1
    y: 1
gates:
  - x: 5
    y: 2
    open_if:
      switch_is_on: sw1
---
xxxxxxx
x  O  x
x P b|x
x^    x
xxxxxxx
---
""")

    destinations = build_possible_destinations(game_map, 4, 2)

    assert center(3, 3) not in destinations
    assert center(5, 2) not in destinations
    assert center(1, 1) in destinations
    assert center(4, 2) in destinations


def test_blob_moves_towards_visible_player(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 7
height: 5
---
xxxxxxx
x     x
x P b x
x     x
xxxxxxx
---
""")

    navmesh = build_navmesh(game_map, 1)
    sprite = make_blob_sprite(4, 2)
    px, py = center(2, 2)
    player = Player(px, py)

    blob = BlobEnemy(
        sprite=sprite,
        navmesh=navmesh,
        navmesh_subdivisions=1,
        possible_destinations=[center(4, 2)],
        rng=random.Random(0),
    )

    context = EnemyUpdateContext(
        player=player,
        line_of_sight_walls=arcade.SpriteList(use_spatial_hash=True),
    )

    old_x = sprite.center_x
    blob.update(context)

    assert blob.destination == center(2, 2)
    assert sprite.center_x < old_x


def test_bush_blocks_blob_line_of_sight(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 7
height: 5
---
xxxxxxx
x     x
x P b x
x     x
xxxxxxx
---
""")

    navmesh = build_navmesh(game_map, 1)
    sprite = make_blob_sprite(4, 2)
    player = Player(*center(2, 2))

    wall = arcade.SpriteSolidColor(
        TILE_SIZE,
        TILE_SIZE,
        center_x=center(3, 2)[0],
        center_y=center(3, 2)[1],
    )
    walls: arcade.SpriteList[arcade.Sprite] = arcade.SpriteList(use_spatial_hash=True)
    walls.append(wall)

    blob = BlobEnemy(
        sprite=sprite,
        navmesh=navmesh,
        navmesh_subdivisions=1,
        possible_destinations=[center(4, 2)],
        rng=random.Random(0),
    )

    context = EnemyUpdateContext(player=player, line_of_sight_walls=walls)

    blob.update(context)

    assert blob.destination == center(4, 2)
    assert sprite.center_x == center(4, 2)[0]
    assert sprite.center_y == center(4, 2)[1]


def test_blob_does_not_chase_player_when_ghost_active(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 7
height: 5
---
xxxxxxx
x     x
x P b x
x     x
xxxxxxx
---
""")

    navmesh = build_navmesh(game_map, 1)
    sprite = make_blob_sprite(4, 2)
    player = Player(*center(2, 2))

    blob = BlobEnemy(
        sprite=sprite,
        navmesh=navmesh,
        navmesh_subdivisions=1,
        possible_destinations=[center(4, 2)],
        rng=random.Random(0),
    )

    context = EnemyUpdateContext(
        player=player,
        line_of_sight_walls=arcade.SpriteList(use_spatial_hash=True),
        is_ghost_active=True,
    )

    blob.update(context)

    assert blob.destination == center(4, 2)


def test_blob_kills_player(window: arcade.Window) -> None:
    game_map = Map.from_string("""width: 7
height: 5
---
xxxxxxx
x     x
x P b x
x     x
xxxxxxx
---
""")
    view = GameView(game_map)
    window.show_view(view)

    blob_sprite = view.blobs[0]
    view.player.center_x = blob_sprite.center_x
    view.player.center_y = blob_sprite.center_y
    view.on_update(1 / 60)

    assert window.current_view is not view
