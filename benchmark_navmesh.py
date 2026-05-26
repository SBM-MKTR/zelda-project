import statistics
import timeit
from pathlib import Path
from collections.abc import Callable
import networkx as nx
from constants import BLOB_NAVMESH_SUBDIVISIONS, TILE_SIZE
from map import Map
from navmesh import NodeType, build_navmesh, find_path


def node_to_pixel(node: NodeType, subdivisions: int) -> tuple[float, float]:
    ix, iy = node
    return (
        (ix + 0.5) * TILE_SIZE / subdivisions,
        (iy + 0.5) * TILE_SIZE / subdivisions,
    )


def make_open_map(width: int, height: int) -> Map:
    rows: list[str] = []

    for y in range(height):
        if y == 0 or y == height - 1:
            rows.append("x" * width)
        else:
            rows.append("x" + " " * (width - 2) + "x")

    player_row = list(rows[height - 2])
    player_row[1] = "P"
    rows[height - 2] = "".join(player_row)

    text = (
        f"width: {width}\n"
        f"height: {height}\n"
        "---\n"
        + "\n".join(rows)
        + "\n---\n"
    )

    return Map.from_string(text)


def measure(
    call: Callable[[], object],
    number: int,
    repeats: int = 7,
) -> tuple[float, float]:
    call()

    timings = [
        timeit.timeit(call, number=number) / number
        for _ in range(repeats)
    ]

    return statistics.mean(timings), statistics.stdev(timings)

def largest_component_endpoints(
    graph: nx.Graph[NodeType],
    subdivisions: int,
) -> tuple[tuple[float, float], tuple[float, float]]:
    unvisited: set[NodeType] = set()

    for node in graph.nodes:
        unvisited.add(node)

    largest_component: set[NodeType] = set()

    while unvisited:
        start_node = unvisited.pop()
        component = {start_node}
        stack = [start_node]

        while stack:
            node = stack.pop()

            for neighbor in graph.neighbors(node):
                if neighbor not in unvisited:
                    continue

                unvisited.remove(neighbor)
                component.add(neighbor)
                stack.append(neighbor)

        if len(component) > len(largest_component):
            largest_component = component

    if not largest_component:
        raise ValueError("cannot benchmark pathfinding on an empty navmesh")

    nodes = list(largest_component)

    start = min(nodes, key=lambda node: node[0] + node[1])
    end = max(nodes, key=lambda node: node[0] + node[1])

    return node_to_pixel(start, subdivisions), node_to_pixel(end, subdivisions)


def benchmark_map(name: str, game_map: Map) -> None:
    n = BLOB_NAVMESH_SUBDIVISIONS

    graph = build_navmesh(game_map, n)
    node_count = len(graph.nodes)
    edge_count = len(graph.edges)

    build_mean, build_stdev = measure(
        lambda: build_navmesh(game_map, n),
        number=20,
    )

    src, dst = largest_component_endpoints(graph, n)

    path_mean, path_stdev = measure(
        lambda: find_path(graph, src[0], src[1], dst[0], dst[1], n),
        number=200,
    )

    print(
        f"{name:>12} | "
        f"{game_map.width:>3}x{game_map.height:<3} | "
        f"{node_count:>5} | "
        f"{edge_count:>6} | "
        f"{build_mean * 1000:>8.4f} ms | "
        f"{build_stdev * 1000:>8.4f} ms | "
        f"{path_mean * 1000:>8.4f} ms | "
        f"{path_stdev * 1000:>8.4f} ms"
    )


def main() -> None:
    maps = [
        ("real map", Map.from_file(Path("Maps/map1.txt"))),
        ("small", make_open_map(12, 8)),
        ("medium", make_open_map(30, 20)),
        ("large", make_open_map(60, 40)),
    ]

    print(f"Navmesh benchmark with subdivisions={BLOB_NAVMESH_SUBDIVISIONS}")
    print()
    print(
        "map          | size   | nodes | edges  | "
        "build mean | build sd  | path mean | path sd"
    )

    for name, game_map in maps:
        benchmark_map(name, game_map)


if __name__ == "__main__":
    main()
