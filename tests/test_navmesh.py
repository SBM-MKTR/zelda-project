import pytest

from constants import TILE_SIZE
from map import Map
from navmesh import build_navmesh, find_path


def center(x: int, y: int) -> tuple[float, float]:
    return x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2


def test_navmesh_rejects_invalid_subdivisions() -> None:
    game_map = Map.from_string("""width: 3
height: 3
---
xxx
xPx
xxx
---
""")

    with pytest.raises(ValueError):
        build_navmesh(game_map, 0)

    with pytest.raises(ValueError):
        build_navmesh(game_map, 2)


def test_navmesh_does_not_create_nodes_on_obstacles() -> None:
    game_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x x x
xP Ox
xxxxx
---
""")

    graph = build_navmesh(game_map, 1)

    assert (1, 1) in graph
    assert (2, 2) not in graph
    assert (3, 1) not in graph


def test_fine_navmesh_removes_nodes_too_close_to_bush_but_not_hole() -> None:
    bush_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x x x
xP  x
xxxxx
---
""")

    hole_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x O x
xP  x
xxxxx
---
""")

    node_close_to_center_obstacle = (5, 7)

    assert node_close_to_center_obstacle not in build_navmesh(bush_map, 3)
    assert node_close_to_center_obstacle in build_navmesh(hole_map, 3)


def test_find_path_avoids_obstacle_nodes() -> None:
    game_map = Map.from_string("""width: 5
height: 5
---
xxxxx
x   x
x O x
xP  x
xxxxx
---
""")

    graph = build_navmesh(game_map, 1)
    path = find_path(graph, *center(1, 2), *center(3, 2), 1)

    assert path[0] == center(1, 2)
    assert path[-1] == center(3, 2)
    assert center(2, 2) not in path


def test_find_path_returns_source_when_no_path_exists() -> None:
    game_map = Map.from_string("""width: 7
height: 5
---
xxxxxxx
x  x  x
xP x  x
x  x  x
xxxxxxx
---
""")

    graph = build_navmesh(game_map, 1)
    path = find_path(graph, *center(1, 2), *center(5, 2), 1)

    assert path == [center(1, 2)]
