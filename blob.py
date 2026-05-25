import random
import math
from dataclasses import dataclass
from map import Map
from map_types import GridCell
from constants import TILE_SIZE
import networkx as nx
from navmesh import find_path, NodeType

PATROL_RADIUS = 3       # demi-côté du carré de patrouille (7 cellules = rayon 3)
BLOB_SPEED = 1.0        # pixels par frame
ARRIVAL_THRESHOLD = 4.0 # distance en pixels pour considérer la destination atteinte
LINE_OF_SIGHT_MAX = 5 * TILE_SIZE


@dataclass
class BlobState:
    start_cell_x: int
    start_cell_y: int
    pos_x: float
    pos_y: float
    destination: tuple[float, float]
    path: list[tuple[float, float]]
    possible_destinations: list[tuple[float, float]]


def build_possible_destinations(game_map: Map, cell_x: int, cell_y: int) -> list[tuple[float, float]]:
    """Calcule les destinations aléatoires possibles d'un blob centré en (cell_x, cell_y)."""
    destinations = []
    for dy in range(-PATROL_RADIUS, PATROL_RADIUS + 1):
        for dx in range(-PATROL_RADIUS, PATROL_RADIUS + 1):
            cx, cy = cell_x + dx, cell_y + dy
            if not (0 <= cx < game_map.width and 0 <= cy < game_map.height):
                continue
            cell = game_map.get(cx, cy)
            if cell not in (GridCell.BUSH, GridCell.HOLE):
                px = (cx + 0.5) * TILE_SIZE
                py = (cy + 0.5) * TILE_SIZE
                destinations.append((px, py))
    return destinations


def pick_new_destination(state: BlobState) -> tuple[float, float]:
    return random.choice(state.possible_destinations)


def update_blob(
    state: BlobState,
    graph: nx.Graph[NodeType],
    n: int,
    player_px: float | None,
) -> BlobState:
    """Met à jour l'état du blob pour une frame.

    player_px/py = position du joueur si visible, None sinon.
    """
    # 1. Mise à jour de la destination
    if player_px is not None:
        new_dest = (player_px, state.destination[1])  # à adapter avec player_py
        new_path = find_path(graph, state.pos_x, state.pos_y, *new_dest, n)
    elif math.hypot(state.pos_x - state.destination[0], state.pos_y - state.destination[1]) < ARRIVAL_THRESHOLD:
        new_dest = pick_new_destination(state)
        new_path = find_path(graph, state.pos_x, state.pos_y, *new_dest, n)
    else:
        new_dest = state.destination
        new_path = state.path

    # 2. Déplacement le long du chemin
    if len(new_path) >= 2:
        next_point = new_path[1]
        dx = next_point[0] - state.pos_x
        dy = next_point[1] - state.pos_y
        dist = math.hypot(dx, dy)
        if dist < BLOB_SPEED:
            new_path = new_path[1:]
            new_pos = (state.pos_x + dx, state.pos_y + dy)
        else:
            new_pos = (state.pos_x + dx / dist * BLOB_SPEED, state.pos_y + dy / dist * BLOB_SPEED)
    else:
        new_pos = (state.pos_x, state.pos_y)

    return BlobState(
        start_cell_x=state.start_cell_x,
        start_cell_y=state.start_cell_y,
        pos_x=new_pos[0],
        pos_y=new_pos[1],
        destination=new_dest,
        path=new_path,
        possible_destinations=state.possible_destinations,
    )
