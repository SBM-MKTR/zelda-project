import math
import random
import arcade
import networkx as nx

from constants import TILE_SIZE
from textures import ANIMATION_BLOB
from navmesh import Node, path_from_positions
from map import Map, GridCell

BLOB_MOVEMENT_SPEED = 1
"""Speed of the blob, in pixels per frame."""

BLOB_DETECTION_RANGE = 5 * TILE_SIZE
"""Maximum distance at which a blob can see the player."""

BLOB_PATROL_HALF = 3
"""Half-side of the patrol square in cells (7x7 square -> half = 3)."""

BLOB_ARRIVAL_THRESHOLD = TILE_SIZE // 3
"""Distance in pixels below which the blob considers it has reached its destination."""


def _blob_patrol_destinations(game_map: Map, start_x: int, start_y: int) -> list[Node]:
    """
    Returns all valid patrol destinations for a blob starting at grid cell
    (start_x, start_y).

    Valid destinations are cells within a 7x7 square centered on the start
    position that:
    - are within map bounds
    - contain no obstacle (no bush, no hole)

    Returns pixel positions (center of each valid cell).
    """
    destinations: list[Node] = []

    for dy in range(-BLOB_PATROL_HALF, BLOB_PATROL_HALF + 1):
        for dx in range(-BLOB_PATROL_HALF, BLOB_PATROL_HALF + 1):
            cx = start_x + dx
            cy = start_y + dy

            if not (0 <= cx < game_map.width and 0 <= cy < game_map.height):
                continue

            cell = game_map.get(cx, cy)
            if cell in (GridCell.BUSH, GridCell.HOLE):
                continue

            px = float(cx * TILE_SIZE + TILE_SIZE // 2)
            py = float(cy * TILE_SIZE + TILE_SIZE // 2)
            destinations.append((px, py))

    return destinations


class Blob(arcade.TextureAnimationSprite):
    """
    A blob enemy that patrols a 7x7 zone and chases the player on sight.

    Attributes:
        __graph:        The navmesh graph used for pathfinding.
        __patrol_dests: Precomputed list of valid patrol destinations.
        __current_path: Current list of waypoints to follow (pixel positions).
        __destination:  Current destination pixel position.
    """

    __graph: nx.Graph[Node]
    __patrol_dests: list[Node]
    __current_path: list[Node]
    __destination: Node

    def __init__(
        self,
        center_x: float,
        center_y: float,
        start_grid_x: int,
        start_grid_y: int,
        game_map: Map,
        graph: nx.Graph[Node],
    ) -> None:
        super().__init__(
            animation=ANIMATION_BLOB,
            scale=TILE_SIZE / 16,
            center_x=center_x,
            center_y=center_y,
        )

        self.__graph = graph
        self.__patrol_dests = _blob_patrol_destinations(game_map, start_grid_x, start_grid_y)
        self.__destination = (center_x, center_y)
        self.__current_path = []

    def __choose_random_destination(self) -> Node:
        """Picks a random valid patrol destination."""
        return random.choice(self.__patrol_dests)

    def __compute_path(self) -> None:
        """Recomputes the path from current position to current destination."""
        self.__current_path = path_from_positions(
            self.__graph,
            self.center_x,
            self.center_y,
            self.__destination[0],
            self.__destination[1],
        )

    def __distance_to_destination(self) -> float:
        """Returns euclidean distance from current position to current destination."""
        dx = self.__destination[0] - self.center_x
        dy = self.__destination[1] - self.center_y
        return math.sqrt(dx * dx + dy * dy)

    def __move_along_path(self) -> None:
        """
        Advances the blob by BLOB_MOVEMENT_SPEED pixels along its current path.
        Pops waypoints that have been reached.
        """
        if not self.__current_path:
            return

        remaining = float(BLOB_MOVEMENT_SPEED)

        while remaining > 0 and self.__current_path:
            target_x, target_y = self.__current_path[0]
            dx = target_x - self.center_x
            dy = target_y - self.center_y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= remaining:
                self.center_x = target_x
                self.center_y = target_y
                remaining -= dist
                self.__current_path.pop(0)
            else:
                self.center_x += dx / dist * remaining
                self.center_y += dy / dist * remaining
                remaining = 0

    def update_blob(self, player: arcade.Sprite, walls: arcade.SpriteList) -> None:
        """
        Main update method to call every frame.

        Args:
            player: The player sprite (used for line-of-sight and chase).
            walls:  The wall sprite list (bushes only, used for line-of-sight).
        """
        # 1. Check line of sight to player
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist_to_player = math.sqrt(dx * dx + dy * dy)

        can_see_player = (
            dist_to_player <= BLOB_DETECTION_RANGE
            and arcade.has_line_of_sight(
                (self.center_x, self.center_y),
                (player.center_x, player.center_y),
                walls,
            )
        )

        if can_see_player:
            # Chase: replace destination with current player position
            self.__destination = (float(player.center_x), float(player.center_y))
            self.__compute_path()
        elif self.__distance_to_destination() <= BLOB_ARRIVAL_THRESHOLD:
            # Patrol: pick a new random destination
            if self.__patrol_dests:
                self.__destination = self.__choose_random_destination()
                self.__compute_path()

        # Move along current path regardless of destination change
        self.__move_along_path()
