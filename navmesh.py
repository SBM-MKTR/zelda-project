import math
import networkx as nx

from map import Map, GridCell
from constants import TILE_SIZE

# 3x3 sub-nodes per cell: positions at 1/6, 3/6, 5/6 of the tile size
_OFFSETS = [TILE_SIZE * k // 6 for k in (1, 3, 5)]

# A node is a (float, float) pixel position
Node = tuple[float, float]


def _node_position(cell_x: int, cell_y: int, ox: int, oy: int) -> Node:
    """Returns the pixel position of a sub-node within a cell."""
    px = cell_x * TILE_SIZE + ox
    py = cell_y * TILE_SIZE + oy
    return (float(px), float(py))


def _is_too_close_to_bush(
    px: float, py: float, game_map: Map
) -> bool:
    """
    Returns True if the pixel position (px, py) is strictly closer than
    TILE_SIZE to the center of any bush cell.
    """
    for cy in range(game_map.height):
        for cx in range(game_map.width):
            if game_map.get(cx, cy) == GridCell.BUSH:
                bush_cx = cx * TILE_SIZE + TILE_SIZE // 2
                bush_cy = cy * TILE_SIZE + TILE_SIZE // 2
                dx = px - bush_cx
                dy = py - bush_cy
                if (dx * dx + dy * dy) < TILE_SIZE * TILE_SIZE:
                    return True
    return False


def build_navmesh(game_map: Map) -> nx.Graph[Node]:
    """
    Builds a navigation graph from a Map.

    Each non-bush cell contributes up to 3x3 sub-nodes, placed at
    positions (1/6, 3/6, 5/6) * TILE_SIZE within the cell.
    Nodes too close (< TILE_SIZE) to any bush center are excluded.

    Edges connect every node to its 8 neighbours (cardinal + diagonal)
    with weight = euclidean distance.

    Returns:
        A networkx Graph whose nodes are (float, float) pixel positions.
    """
    graph: nx.Graph[Node] = nx.Graph()

    # --- 1. Add nodes ---
    for cy in range(game_map.height):
        for cx in range(game_map.width):
            if game_map.get(cx, cy) == GridCell.BUSH:
                continue  # no nodes inside bushes

            for oy in _OFFSETS:
                for ox in _OFFSETS:
                    px, py = _node_position(cx, cy, ox, oy)
                    if not _is_too_close_to_bush(px, py, game_map):
                        graph.add_node((px, py))

    # --- 2. Add edges between neighbouring nodes ---
    nodes = list(graph.nodes)
    # Build a set for O(1) lookup
    node_set: set[Node] = set(nodes)

    # The step between adjacent sub-nodes (within or across cells)
    step = TILE_SIZE // 3  # = TILE_SIZE * 2/6, distance between adjacent offsets

    for node in nodes:
        px, py = node
        for dy in (-step, 0, step):
            for dx in (-step, 0, step):
                if dx == 0 and dy == 0:
                    continue
                neighbour: Node = (px + dx, py + dy)
                if neighbour in node_set:
                    dist = math.sqrt(dx * dx + dy * dy)
                    graph.add_edge(node, neighbour, weight=dist)

    return graph


def nearest_node(graph: nx.Graph[Node], px: float, py: float) -> Node | None:
    """
    Returns the graph node closest (euclidean) to pixel position (px, py).
    Returns None if the graph is empty.
    """
    best: Node | None = None
    best_dist = float("inf")

    for node in graph.nodes:
        nx_, ny = node
        d = (px - nx_) ** 2 + (py - ny) ** 2
        if d < best_dist:
            best_dist = d
            best = node

    return best


def find_path(
    graph: nx.Graph[Node], start: Node, end: Node
) -> list[Node]:
    """
    Finds the shortest weighted path between two nodes using Dijkstra.

    Args:
        graph: The navmesh graph.
        start: Starting pixel position (must be a node in the graph).
        end:   Target pixel position (must be a node in the graph).

    Returns:
        A list of (float, float) pixel positions from start to end
        (inclusive). Returns [start] if start == end or no path exists.
    """
    if start == end:
        return [start]

    try:
        return nx.dijkstra_path(graph, start, end, weight="weight")
    except nx.NetworkXNoPath:
        return [start]


def path_from_positions(
    graph: nx.Graph[Node], from_px: float, from_py: float, to_px: float, to_py: float
) -> list[Node]:
    """
    High-level helper: finds a path in pixel space from any position to
    any destination, snapping both endpoints to the nearest graph nodes.

    Returns a list of (float, float) waypoints to follow, starting with
    the nearest node to the origin and ending with the nearest node to
    the destination. Returns an empty list if no path can be found.
    """
    start_node = nearest_node(graph, from_px, from_py)
    end_node = nearest_node(graph, to_px, to_py)

    if start_node is None or end_node is None:
        return []

    return find_path(graph, start_node, end_node)
