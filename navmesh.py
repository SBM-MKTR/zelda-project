import math
import networkx as nx
from map_types import GridCell
from map import Map
from constants import TILE_SIZE

NodeType = tuple[int, int]

BLOB_DESTINATION_OBSTACLES = (
    GridCell.BUSH,
    GridCell.HOLE,
    GridCell.GATE,
)


def _node_pixel_position(ix: int, iy: int, n: int) -> tuple[float, float]:
    s = TILE_SIZE
    x = (ix + 0.5) * s / n
    y = (iy + 0.5) * s / n
    return x, y


def build_navmesh(game_map: Map, n: int = 1) -> nx.Graph[NodeType]:
    """Builds navmesh for blobs.
    Returns a NetworkX graph where nodes are tuples (ix, iy)
    and edges have a 'weight' attribute = euclidean distance.
    """
    if n < 1 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")

    graph: nx.Graph[NodeType] = nx.Graph()
    s = TILE_SIZE

    total_ix = game_map.width * n
    total_iy = game_map.height * n

    for iy in range(total_iy):
        for ix in range(total_ix):
            cell_x = ix // n
            cell_y = iy // n

            if game_map.get(cell_x, cell_y) in BLOB_DESTINATION_OBSTACLES:
                continue

            if n > 1:
                px, py = _node_pixel_position(ix, iy, n)
                too_close = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx_cell = cell_x + dx
                        ny_cell = cell_y + dy
                        if not (0 <= nx_cell < game_map.width and 0 <= ny_cell < game_map.height):
                            continue
                        if game_map.get(nx_cell, ny_cell) == GridCell.BUSH:
                            bush_px = (nx_cell + 0.5) * s
                            bush_py = (ny_cell + 0.5) * s
                            dist = math.hypot(px - bush_px, py - bush_py)
                            if dist < s: # Ignores nodes closer than one tile to a wall (keeps blobs from cutting off corners)
                                too_close = True
                                break
                    if too_close:
                        break
                if too_close:
                    continue

            graph.add_node((ix, iy))

    for (ix, iy) in list(graph.nodes):
        px, py = _node_pixel_position(ix, iy, n)
        for diy in (-1, 0, 1):
            for dix in (-1, 0, 1):
                if dix == 0 and diy == 0:
                    continue
                nix, niy = ix + dix, iy + diy
                if (nix, niy) in graph.nodes:
                    npx, npy = _node_pixel_position(nix, niy, n)
                    weight = math.hypot(px - npx, py - npy)
                    graph.add_edge((ix, iy), (nix, niy), weight=weight)

    return graph


def nearest_node(graph: nx.Graph[NodeType], px: float, py: float, n: int) -> NodeType:
    if len(graph.nodes) == 0:
        raise ValueError("navmesh is empty, cannot find nearest node")

    return min(
        graph.nodes,
        key=lambda node: math.dist((px, py), _node_pixel_position(node[0], node[1], n)),
    )

def find_path(
    graph: nx.Graph[NodeType],
    src_px: float,
    src_py: float,
    dst_px: float,
    dst_py: float,
    n: int,
) -> list[tuple[float, float]]:
    src_node = nearest_node(graph, src_px, src_py, n)
    dst_node = nearest_node(graph, dst_px, dst_py, n)

    try:
        node_path = nx.dijkstra_path(graph, src_node, dst_node, weight="weight")
    except nx.NetworkXNoPath:
        return [(src_px, src_py)]

    pixel_path: list[tuple[float, float]] = [(src_px, src_py)]

    for node in node_path[1:]:
        ix, iy = node
        pixel_path.append(_node_pixel_position(ix, iy, n))

    pixel_path.append((dst_px, dst_py))
    return pixel_path
