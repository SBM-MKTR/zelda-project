from dataclasses import dataclass, field
import math
import random

import arcade
import networkx as nx

from constants import (
    BLOB_ARRIVAL_THRESHOLD,
    BLOB_LINE_OF_SIGHT_MAX,
    BLOB_MOVEMENT_SPEED,
    BLOB_PATROL_RADIUS,
    TILE_SIZE,
)
from enemies import Enemy, EnemyUpdateContext
from map import Map
from map_types import GridCell
from navmesh import NodeType, find_path
from power_system import PowerSystem


Position = tuple[float, float]
Path = list[Position]

BLOB_DESTINATION_OBSTACLES = (
    GridCell.BUSH,
    GridCell.HOLE,
    GridCell.GATE,
)


def _cell_center(cell_x: int, cell_y: int) -> Position:
    return (
        (cell_x + 0.5) * TILE_SIZE,
        (cell_y + 0.5) * TILE_SIZE,
    )


def build_possible_destinations(
    game_map: Map,
    cell_x: int,
    cell_y: int,
) -> list[Position]:
    destinations: list[Position] = []

    for dy in range(-BLOB_PATROL_RADIUS, BLOB_PATROL_RADIUS + 1):
        for dx in range(-BLOB_PATROL_RADIUS, BLOB_PATROL_RADIUS + 1):
            x = cell_x + dx
            y = cell_y + dy

            if not (0 <= x < game_map.width and 0 <= y < game_map.height):
                continue

            if game_map.get(x, y) in BLOB_DESTINATION_OBSTACLES:
                continue

            destinations.append(_cell_center(x, y))

    return destinations


@dataclass
class BlobEnemy(Enemy):
    """An enemy that patrols randomly using a navmesh
    and chases the player when it sees him."""
    sprite: arcade.TextureAnimationSprite
    navmesh: nx.Graph[NodeType]
    navmesh_subdivisions: int
    possible_destinations: list[Position]
    rng: random.Random = field(default_factory=random.Random)
    destination: Position = field(init=False)
    path: Path = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        if not self.possible_destinations:
            self.possible_destinations = [self._position()]

        self.destination = self._pick_new_destination()
        self._refresh_path()

    def update(self, context: EnemyUpdateContext) -> None:
        """Each frame: chases the player if visible, otherwise patrols to a random destination,
        moving with the navmesh."""
        previous_destination = self.destination
        visible_player_position = self._visible_player_position(context)

        if visible_player_position is not None and not context.is_ghost_active:
            self.destination = visible_player_position
        elif self._has_arrived():
            self.destination = self._pick_new_destination()

        if self.destination != previous_destination or len(self.path) < 2: #Recompute the path if the destination changed or if the path is finished.
            self._refresh_path()

        self._advance_along_path()

    def _position(self) -> Position:
        return self.sprite.center_x, self.sprite.center_y

    def _pick_new_destination(self) -> Position:
        return self.rng.choice(self.possible_destinations)

    def _has_arrived(self) -> bool:
        return (
            math.hypot(
                self.sprite.center_x - self.destination[0],
                self.sprite.center_y - self.destination[1],
            )
            <= BLOB_ARRIVAL_THRESHOLD
        )

    def _visible_player_position(
        self,
        context: EnemyUpdateContext,
    ) -> Position | None:
        observer = self._position()
        target = (context.player.center_x, context.player.center_y)

        if arcade.has_line_of_sight(
            observer,
            target,
            context.line_of_sight_walls,
            max_distance=BLOB_LINE_OF_SIGHT_MAX,
        ):
            return target

        return None

    def _refresh_path(self) -> None:
        self.path = find_path(
            self.navmesh,
            self.sprite.center_x,
            self.sprite.center_y,
            self.destination[0],
            self.destination[1],
            self.navmesh_subdivisions,
        )

    def _advance_along_path(self) -> None:
        while len(self.path) >= 2:
            next_x, next_y = self.path[1]
            dx = next_x - self.sprite.center_x
            dy = next_y - self.sprite.center_y
            distance = math.hypot(dx, dy)

            if distance <= BLOB_MOVEMENT_SPEED:
                self.sprite.center_x = next_x
                self.sprite.center_y = next_y
                self.path = self.path[1:]
                continue

            self.sprite.center_x += dx / distance * BLOB_MOVEMENT_SPEED
            self.sprite.center_y += dy / distance * BLOB_MOVEMENT_SPEED
            return
