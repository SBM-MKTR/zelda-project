from typing import Final
from enum import Enum

class GridCell(Enum):
    GRASS = "grass"
    BUSH = "bush"
    CRYSTAL = "crystal"
    SPINNER_HORIZONTAL = "spinner_horizontal"
    SPINNER_VERTICAL = "spinner_vertical"

class Map:
    __width: Final[int]
    __height: Final[int]
    __player_start_x: Final[int]
    __player_start_y: Final[int]
    __grid: Final[tuple[tuple[GridCell, ...], ...]]

    def __init__(self, width: int, height: int, player_start_x: int, player_start_y: int, grid: list[list[GridCell]] | tuple[tuple[GridCell, ...], ...] ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be > 0")

        if not (0 <= player_start_x < width and 0 <= player_start_y < height):
            raise ValueError("player start out of bounds")

        if len(grid) != height or any(len(row) != width for row in grid):
            raise ValueError("grid size does not match width/height")

        self.__width = width
        self.__height = height
        self.__player_start_x = player_start_x
        self.__player_start_y = player_start_y
        self.__grid = tuple(tuple(row) for row in grid)

    @property
    def width(self) -> int:
            return self.__width

    @property
    def height(self) -> int:
            return self.__height

    @property
    def player_start_x(self) -> int:
            return self.__player_start_x

    @property
    def player_start_y(self) -> int:
            return self.__player_start_y

    def get(self, x : int, y :int) -> GridCell:
        if not(0 <= x < self.__width and 0 <= y < self.__height):
            raise ValueError(f" cell ({x},{y}) is out of bound")
        return self.__grid[y][x]


WIDTH = 40
HEIGHT = 20

grid = [[GridCell.GRASS for _ in range(WIDTH)] for _ in range(HEIGHT)]

# bordures en buissons
for x in range(WIDTH):
    grid[0][x] = GridCell.BUSH
    grid[HEIGHT - 1][x] = GridCell.BUSH

for y in range(HEIGHT):
    grid[y][0] = GridCell.BUSH
    grid[y][WIDTH - 1] = GridCell.BUSH

# buissons internes
for x, y in [(3, 6), (7, 2), (2, 10), (3, 8)]:
    grid[y][x] = GridCell.BUSH

# cristaux
for x, y in [(5, 2), (6, 5), (3, 5)]:
    grid[y][x] = GridCell.CRYSTAL

MAP_DECOUVERTE: Final[Map] = Map(
    width=WIDTH,
    height=HEIGHT,
    player_start_x=2,
    player_start_y=2,
    grid=grid,
)
