from collections.abc import Iterator
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
    KeyConfig,
    ChestConfig,
    InvalidMapFileException,
)
from map_parser import (
    parse_header,
    parse_map_rows,
    build_grid,
    parse_switches,
    parse_gates,
    parse_teleporters,
    parse_keys,
    parse_chests,
    validate_formula,
)


class Map:
    """Parsed and validated game map: grid of cells, player start position,
    and entity configs (switches, gates, teleporters, keys, chests)."""
    __width: Final[int]
    __height: Final[int]
    __player_start_x: Final[int]
    __player_start_y: Final[int]
    __grid: Final[tuple[tuple[GridCell, ...], ...]]
    __switch_configs: Final[tuple[SwitchConfig, ...]]
    __gate_configs: Final[tuple[GateConfig, ...]]
    __teleporter_configs: Final[tuple[TeleporterConfig, ...]]
    __key_configs: Final[tuple[KeyConfig, ...]]
    __chest_configs: Final[tuple[ChestConfig, ...]]

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
        key_configs: tuple[KeyConfig, ...] = (),
        chest_configs: tuple[ChestConfig, ...] = (),
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
        self.__key_configs = key_configs
        self.__chest_configs = chest_configs

        self._validate_entity_positions()


    def _validate_entity_group(
        self,
        configs: tuple[SwitchConfig | GateConfig | TeleporterConfig | KeyConfig | ChestConfig, ...],
        expected_cell: GridCell,
        entity_name: str,
    ) -> set[tuple[int, int]]:
        """Validates a group of entities: boundaries, cell type, unique positions.
        Returns the set of validated positions.
        """
        seen: set[tuple[int, int]] = set()
        for config in configs:
            x, y = config.x, config.y
            entity_id = getattr(config, "id", None)
            label = f"{entity_name} {entity_id!r}" if entity_id is not None else entity_name

            if not (0 <= x < self.__width and 0 <= y < self.__height):
                raise InvalidMapFileException(
                    f"{label} position ({x},{y}) is out of bounds"
                )
            if self.__grid[y][x] != expected_cell:
                raise InvalidMapFileException(
                    f"{label} at ({x},{y}) does not point to a {expected_cell.name} cell"
                )
            pos = (x, y)
            if pos in seen:
                raise InvalidMapFileException(
                    f"two {entity_name}s share the same position ({x},{y})"
                )
            seen.add(pos)
        return seen

    def _validate_entity_positions(self) -> None:
        """Checks that every config must point to the correct cell type,
        and every special cell must have a matching config.
        Raises InvalidMapFileException if any mismatch is found."""
        switch_positions = self._validate_entity_group(
            self.__switch_configs, GridCell.SWITCH, "switch"
        )
        gate_positions = self._validate_entity_group(
            self.__gate_configs, GridCell.GATE, "gate"
        )
        teleporter_positions = self._validate_entity_group(
            self.__teleporter_configs, GridCell.TELEPORTER, "teleporter"
        )
        key_positions = self._validate_entity_group(
            self.__key_configs, GridCell.KEY, "key"
        )
        chest_positions = self._validate_entity_group(
            self.__chest_configs, GridCell.CHEST, "chest"
        )

        for x, y, cell in self.cells():
            match cell:
                    case GridCell.SWITCH if (x, y) not in switch_positions:
                        raise InvalidMapFileException(
                            f"SWITCH cell at ({x},{y}) has no corresponding switch config"
                        )
                    case GridCell.GATE if (x, y) not in gate_positions:
                        raise InvalidMapFileException(
                            f"GATE cell at ({x},{y}) has no corresponding gate config"
                        )
                    case GridCell.TELEPORTER if (x, y) not in teleporter_positions:
                        raise InvalidMapFileException(
                            f"TELEPORTER cell at ({x},{y}) has no corresponding teleporter config"
                        )
                    case GridCell.KEY if (x, y) not in key_positions:
                        raise InvalidMapFileException(
                            f"KEY cell at ({x},{y}) has no corresponding key config"
                        )
                    case GridCell.CHEST if (x, y) not in chest_positions:
                        raise InvalidMapFileException(
                            f"CHEST cell at ({x},{y}) has no corresponding chest config"
                        )
                    case _:
                        continue

    def cells(self) -> Iterator[tuple[int, int, GridCell]]:
        """Yields (x, y, cell) for every cell in the map, row by row."""
        for y in range(self.__height):
            for x in range(self.__width):
                yield x, y, self.__grid[y][x]

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

    @property
    def key_configs(self) -> tuple[KeyConfig, ...]:
        return self.__key_configs

    @property
    def chest_configs(self) -> tuple[ChestConfig, ...]:
        return self.__chest_configs

    def get(self, x: int, y: int) -> GridCell:
        if not (0 <= x < self.__width and 0 <= y < self.__height):
            raise ValueError(f"cell ({x},{y}) is out of bounds")
        return self.__grid[y][x]

    @classmethod
    def from_file(cls, path: str | Path) -> "Map":
        return cls.from_string(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_string(cls, text: str) -> "Map":
        """Parses a full map text (YAML header + grid body)
        and returns a validated Map."""
        lines = text.rstrip("\n").splitlines()

        header = parse_header(lines)
        raw_map_rows = parse_map_rows(lines, header.map_start_index, header.height)
        player_start_x, player_start_y, grid = build_grid(
            raw_map_rows, header.width, header.height
        )

        switch_configs = parse_switches(header.switches_data)
        gate_configs = parse_gates(header.gates_data)
        teleporter_configs = parse_teleporters(header.teleporters_data)
        key_configs = parse_keys(header.keys_data)
        chest_configs = parse_chests(header.chests_data, {kc.id for kc in key_configs})

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
            key_configs=key_configs,
            chest_configs=chest_configs,
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
