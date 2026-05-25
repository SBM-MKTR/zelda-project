from pathlib import Path
from typing import Final

from constants import TILE_SIZE
from map_types import (
    GridCell,
    SpinnerBounds,
    BatBounds,
    SwitchConfig,
    GateConfig,
    TeleporterConfig,
    InvalidMapFileException,
)
from map_parser import (
    parse_header,
    parse_map_rows,
    build_grid,
    parse_switches,
    parse_gates,
    parse_teleporters,
    evaluate_formula,
    validate_formula,
)


class Map:
    __width: Final[int]
    __height: Final[int]
    __player_start_x: Final[int]
    __player_start_y: Final[int]
    __grid: Final[tuple[tuple[GridCell, ...], ...]]
    __switch_configs: Final[tuple[SwitchConfig, ...]]
    __gate_configs: Final[tuple[GateConfig, ...]]
    __teleporter_configs: Final[tuple[TeleporterConfig, ...]]

    def __init__(
        self,
        width: int,
        height: int,
        player_start_x: int,
        player_start_y: int,
        grid: list[list[GridCell]] | tuple[tuple[GridCell, ...], ...],
        switch_configs: tuple[SwitchConfig, ...],
        gate_configs: tuple[GateConfig, ...],
        teleporter_configs: tuple[TeleporterConfig, ...] = (),
    ) -> None:
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
        self.__switch_configs = switch_configs
        self.__gate_configs = gate_configs
        self.__teleporter_configs = teleporter_configs

        self._validate_entity_positions()


    def _validate_entity_positions(self) -> None:
        switch_positions: set[tuple[int, int]] = set()
        for sc in self.__switch_configs:
            if not (0 <= sc.x < self.__width and 0 <= sc.y < self.__height):
                raise InvalidMapFileException(
                    f"switch '{sc.id}' position ({sc.x},{sc.y}) is out of bounds"
                )
            if self.__grid[sc.y][sc.x] != GridCell.SWITCH:
                raise InvalidMapFileException(
                    f"switch '{sc.id}' at ({sc.x},{sc.y}) does not point to a SWITCH cell"
                )
            pos = (sc.x, sc.y)
            if pos in switch_positions:
                raise InvalidMapFileException(
                    f"two switches share the same position ({sc.x},{sc.y})"
                )
            switch_positions.add(pos)

        gate_positions: set[tuple[int, int]] = set()
        for gc in self.__gate_configs:
            if not (0 <= gc.x < self.__width and 0 <= gc.y < self.__height):
                raise InvalidMapFileException(
                    f"gate position ({gc.x},{gc.y}) is out of bounds"
                )
            if self.__grid[gc.y][gc.x] != GridCell.GATE:
                raise InvalidMapFileException(
                    f"gate at ({gc.x},{gc.y}) does not point to a GATE cell"
                )
            pos = (gc.x, gc.y)
            if pos in gate_positions:
                raise InvalidMapFileException(
                    f"two gates share the same position ({gc.x},{gc.y})"
                )
            gate_positions.add(pos)

        for y in range(self.__height):
            for x in range(self.__width):
                cell = self.__grid[y][x]
                if cell == GridCell.SWITCH and (x, y) not in switch_positions:
                    raise InvalidMapFileException(
                        f"SWITCH cell at ({x},{y}) has no corresponding switch config"
                    )
                if cell == GridCell.GATE and (x, y) not in gate_positions:
                    raise InvalidMapFileException(
                        f"GATE cell at ({x},{y}) has no corresponding gate config"
                    )

        teleporter_positions: set[tuple[int, int]] = set()
        for tc in self.__teleporter_configs:
            if not (0 <= tc.x < self.__width and 0 <= tc.y < self.__height):
                raise InvalidMapFileException(
                    f"teleporter {tc.id!r} position ({tc.x},{tc.y}) is out of bounds"
                )
            if self.__grid[tc.y][tc.x] != GridCell.TELEPORTER:
                raise InvalidMapFileException(
                    f"teleporter {tc.id!r} at ({tc.x},{tc.y}) does not point to a TELEPORTER cell"
                )
            pos = (tc.x, tc.y)
            if pos in teleporter_positions:
                raise InvalidMapFileException(
                    f"two teleporters share the same position ({tc.x},{tc.y})"
                )
            teleporter_positions.add(pos)

        for y in range(self.__height):
            for x in range(self.__width):
                if self.__grid[y][x] == GridCell.TELEPORTER and (x, y) not in teleporter_positions:
                    raise InvalidMapFileException(
                        f"TELEPORTER cell at ({x},{y}) has no corresponding teleporter config"
                    )

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

    @property
    def switch_configs(self) -> tuple[SwitchConfig, ...]:
        return self.__switch_configs

    @property
    def gate_configs(self) -> tuple[GateConfig, ...]:
        return self.__gate_configs

    @property
    def teleporter_configs(self) -> tuple[TeleporterConfig, ...]:
        return self.__teleporter_configs

    def get(self, x: int, y: int) -> GridCell:
        if not (0 <= x < self.__width and 0 <= y < self.__height):
            raise ValueError(f"cell ({x},{y}) is out of bounds")
        return self.__grid[y][x]

    @classmethod
    def from_file(cls, path: str | Path) -> "Map":
        return cls.from_string(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_string(cls, text: str) -> "Map":
        lines = text.rstrip("\n").splitlines()

        header = parse_header(lines)
        raw_map_rows = parse_map_rows(lines, header.map_start_index, header.height)
        player_start_x, player_start_y, grid = build_grid(
            raw_map_rows, header.width, header.height
        )

        switch_configs = parse_switches(header.switches_data)
        gate_configs = parse_gates(header.gates_data)
        teleporter_configs = parse_teleporters(header.teleporters_data)

        known_ids = {sc.id for sc in switch_configs}
        for gc in gate_configs:
            validate_formula(gc.open_if, known_ids)

        return cls(
            width=header.width,
            height=header.height,
            player_start_x=player_start_x,
            player_start_y=player_start_y,
            grid=grid,
            switch_configs=switch_configs,
            gate_configs=gate_configs,
            teleporter_configs=teleporter_configs,
        )


def spinner_bounds(game_map: Map, x: int, y: int) -> SpinnerBounds:
    cell = game_map.get(x, y)

    if cell == GridCell.SPINNER_HORIZONTAL:
        min_x = x
        while min_x > 0 and game_map.get(min_x - 1, y) != GridCell.BUSH:
            min_x -= 1

        max_x = x
        while max_x < game_map.width - 1 and game_map.get(max_x + 1, y) != GridCell.BUSH:
            max_x += 1

        return SpinnerBounds(min_x=min_x, max_x=max_x, min_y=y, max_y=y)

    if cell == GridCell.SPINNER_VERTICAL:
        min_y = y
        while min_y > 0 and game_map.get(x, min_y - 1) != GridCell.BUSH:
            min_y -= 1

        max_y = y
        while max_y < game_map.height - 1 and game_map.get(x, max_y + 1) != GridCell.BUSH:
            max_y += 1

        return SpinnerBounds(min_x=x, max_x=x, min_y=min_y, max_y=max_y)

    raise ValueError(f"cell ({x}, {y}) is not a spinner")


def bat_bounds(game_map: Map, x: int, y: int, radius: float) -> BatBounds:
    cell = game_map.get(x, y)
    if cell != GridCell.BAT:
        raise ValueError(f"cell ({x}, {y}) is not a bat")

    center_x = x * TILE_SIZE + TILE_SIZE // 2
    center_y = y * TILE_SIZE + TILE_SIZE // 2
    return BatBounds(center_x=center_x, center_y=center_y, radius=radius)
