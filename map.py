
from enum import Enum
from pathlib import Path
from typing import Final
from dataclasses import dataclass
from constants import *
import yaml


class InvalidMapFileException(Exception):
    pass

class GridCell(Enum):
    GRASS = "grass"
    BUSH = "bush"
    CRYSTAL = "crystal"
    SPINNER_HORIZONTAL = "spinner_horizontal"
    SPINNER_VERTICAL = "spinner_vertical"
    HOLE = "hole"
    BAT = "bat"
    BLOB = "blob"
    SWITCH = "switch"
    GATE = "gate"

@dataclass(frozen=True)
class SpinnerBounds:
    min_x: int
    max_x: int
    min_y: int
    max_y: int

@dataclass(frozen=True)
class BatBounds:
    center_x: float
    center_y: float
    rayon: float

@dataclass(frozen=True)
class SwitchConfig:
    id: str
    x: int
    y: int
    state: bool

@dataclass(frozen=True)
class GateConfig:
    x: int
    y: int
    open_if: dict


class Map:
    __width: Final[int]
    __height: Final[int]
    __player_start_x: Final[int]
    __player_start_y: Final[int]
    __grid: Final[tuple[tuple[GridCell, ...], ...]]
    __switch_configs: Final[list[SwitchConfig]]
    __gate_configs: Final[list[GateConfig]]

    def __init__(self, width: int, height: int, player_start_x: int, player_start_y: int, grid: list[list[GridCell]] | tuple[tuple[GridCell, ...], ...], switch_configs: list[SwitchConfig], gate_configs: list[GateConfig]) -> None:
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
    def switch_configs(self) -> list[SwitchConfig]:
        return self.__switch_configs #est ce qu'on met list(self.__switch_configs) ?

    @property
    def gate_configs(self) -> list[GateConfig]:
        return self.__gate_configs #idem

    def get(self, x : int, y :int) -> GridCell:
        if not(0 <= x < self.__width and 0 <= y < self.__height):
            raise ValueError(f" cell ({x},{y}) is out of bound")
        return self.__grid[y][x]

    @classmethod
    def from_file(cls, path: str | Path) -> "Map":
        return cls.from_string(Path(path).read_text(encoding="utf-8"))

    @classmethod
    def from_string(cls, text: str) -> "Map":
        lines = text.splitlines()

        width, height, switches_data, gates_data, map_start_index = cls._parse_header(lines)
        raw_map_rows = cls._parse_map_rows(lines, map_start_index, height)
        player_start_x, player_start_y, grid = cls._build_grid(
            raw_map_rows, width, height
        )

        return cls(
            width=width,
            height=height,
            player_start_x=player_start_x,
            player_start_y=player_start_y,
            grid=grid,
            switch_configs=parse_switches(switches_data),
            gate_configs=parse_gates(gates_data),
        )

    @staticmethod #est ce que on gère les clefs dupliquées comme la previous version cidessous ?
    def _parse_header(lines: list[str]) -> tuple[int, int, list, list, int]:

        if not lines:
            raise InvalidMapFileException("empty map file")

        try:
            separator_index = lines.index("---")
        except ValueError:
            raise InvalidMapFileException("missing configuration terminator '---'")

        yaml_text = "\n".join(lines[:separator_index])
        try:
            config = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            raise InvalidMapFileException(f"invalid YAML in header: {e}")

        if not isinstance(config, dict):
            raise InvalidMapFileException("configuration must be a YAML mapping")

        for key in ("width", "height"):
            if key not in config:
                raise InvalidMapFileException(f"missing configuration key: {key!r}")
            if not isinstance(config[key], int) or config[key] <= 0:
                raise InvalidMapFileException(f"{key} must be a strictly positive integer")

        width = config["width"]
        height = config["height"]

        switches: list = config.get("switches", [])
        gates: list = config.get("gates", [])

        if switches is None:
            switches = []
        if gates is None:
            gates = []

        if not isinstance(switches, list):
            raise InvalidMapFileException("'switches' must be a list")
        if not isinstance(gates, list):
            raise InvalidMapFileException("'gates' must be a list")

        return width, height, switches, gates, separator_index + 1

        """if not lines:
            raise InvalidMapFileException("empty map file")

        config: dict[str, str] = {}
        index = 0

        while index < len(lines) and lines[index] != "---":
            line = lines[index]
            key, separator, value = line.partition(": ")

            if separator == "" or key == "" or value == "":
                raise InvalidMapFileException(
                    f"invalid configuration line: {line!r}"
                )

            if key in config:
                raise InvalidMapFileException(
                    f"duplicate configuration key: {key!r}"
                )

            config[key] = value
            index += 1

        if index == len(lines):
            raise InvalidMapFileException(
                "missing configuration terminator '---'"
            )

        width = Map._parse_positive_int(config, "width")
        height = Map._parse_positive_int(config, "height")

        return width, height, index + 1"""

    @staticmethod
    def _parse_positive_int(config: dict[str, str], key: str) -> int:
        if key not in config:
            raise InvalidMapFileException(f"missing configuration key: {key!r}")

        value = config[key]

        if not value.isdigit():
            raise InvalidMapFileException(
                f"{key} must be a positive base-10 integer"
            )

        integer_value = int(value)

        if integer_value <= 0:
            raise InvalidMapFileException(
                f"{key} must be strictly positive"
            )

        return integer_value

    @staticmethod
    def _parse_map_rows(
        lines: list[str], map_start_index: int, height: int
    ) -> list[str]:
        final_terminator_index = map_start_index + height

        if len(lines) < final_terminator_index + 1:
            raise InvalidMapFileException(
                "map section does not contain the expected number of lines"
            )

        raw_map_rows = lines[map_start_index:final_terminator_index]

        if lines[final_terminator_index] != "---":
            raise InvalidMapFileException("missing final terminator '---'")

        if len(lines) != final_terminator_index + 1:
            raise InvalidMapFileException(
                "extra content after final terminator"
            )

        return raw_map_rows

    @staticmethod
    def _build_grid(
        raw_map_rows: list[str], width: int, height: int
    ) -> tuple[int, int, list[list[GridCell]]]:
        grid = [
            [GridCell.GRASS for _ in range(width)]
            for _ in range(height)
        ]

        player_position: tuple[int, int] | None = None

        for visual_row_index, raw_row in enumerate(raw_map_rows):
            if len(raw_row) > width:
                raise InvalidMapFileException(
                    f"map row too long: expected at most {width} characters, got {len(raw_row)}"
                )

            y = height - 1 - visual_row_index

            for x, char in enumerate(raw_row):
                if char == "P":
                    if player_position is not None:
                        raise InvalidMapFileException(
                            "map must contain exactly one 'P'"
                        )
                    player_position = (x, y)
                    continue

                grid[y][x] = Map._cell_from_char(char)

        if player_position is None:
            raise InvalidMapFileException(
                "map must contain exactly one 'P'"
            )

        return player_position[0], player_position[1], grid

    @staticmethod
    def _cell_from_char(char: str) -> GridCell:
        match char:
            case " ":
                return GridCell.GRASS
            case "x":
                return GridCell.BUSH
            case "*":
                return GridCell.CRYSTAL
            case "s":
                return GridCell.SPINNER_HORIZONTAL
            case "S":
                return GridCell.SPINNER_VERTICAL
            case "O":
                return GridCell.HOLE
            case "v":
                return GridCell.BAT
            case "b":
                return GridCell.BLOB
            case "^":
                return GridCell.SWITCH
            case "|":
                return GridCell.GATE
            case _:
                raise InvalidMapFileException(
                    f"invalid map character: {char!r}"
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

        return SpinnerBounds(
            min_x=min_x,
            max_x=max_x,
            min_y=y,
            max_y=y,
        )

    if cell == GridCell.SPINNER_VERTICAL:
        min_y = y
        while min_y > 0 and game_map.get(x, min_y - 1) != GridCell.BUSH:
            min_y -= 1

        max_y = y
        while max_y < game_map.height - 1 and game_map.get(x, max_y + 1) != GridCell.BUSH:
            max_y += 1

        return SpinnerBounds(
            min_x=x,
            max_x=x,
            min_y=min_y,
            max_y=max_y,
        )

    raise ValueError(f"cell ({x}, {y}) is not a spinner")

def bat_bounds(game_map: Map, x: int, y: int, rayon: float) -> BatBounds:
    cell = game_map.get(x, y)
    if cell != GridCell.BAT:
        raise ValueError(f"cell ({x}, {y}) is not a bat")

    center_x = x * TILE_SIZE + TILE_SIZE // 2
    center_y = y * TILE_SIZE + TILE_SIZE // 2
    return BatBounds(
        center_x = center_x,
        center_y = center_y,
        rayon = rayon,
    )

def parse_switches(data: list) -> list[SwitchConfig]:
    result = []
    for item in data:
        if not isinstance(item, dict):
            raise InvalidMapFileException("each switch must be a mapping")
        for key in ("id", "x", "y"):
            if key not in item:
                raise InvalidMapFileException(f"switch missing key: {key!r}")
        state_try = item.get("state", False)
        if not isinstance (state_try, bool):
            raise InvalidMapFileException(f"switch state must be 'on' or 'off', got {state_try!r}")
        result.append(SwitchConfig(
            id=item["id"],
            x=item["x"],
            y=item["y"],
            state=state_try,
        ))
    return result

def parse_gates(data: list) -> list[GateConfig]:
    result = []
    for item in data:
        if not isinstance(item, dict):
            raise InvalidMapFileException("each gate must be a mapping")
        for key in ("x", "y", "open_if"):
            if key not in item:
                raise InvalidMapFileException(f"gate missing key: {key!r}")
        result.append(GateConfig(
            x=item["x"],
            y=item["y"],
            open_if=item["open_if"],
        ))
    return result

def evaluate_formula(formula: dict, switch_states: dict[str, bool]) -> bool:
    if not isinstance(formula, dict) or len(formula) != 1:
        raise InvalidMapFileException("a formula must be a dict with exactly one key")

    key, value = next(iter(formula.items()))
    """for k, v in formula.items():
           key = k
           value = v
           break"""

    match key:
        case "switch_is_on":
            if value not in switch_states:
                raise InvalidMapFileException(f"unknown switch id: {value!r}")
            return switch_states[value]
        case "not":
            if not isinstance(value, list) or len(value) != 1:
                raise InvalidMapFileException("'not' must have exactly one element")
            return not evaluate_formula(value[0], switch_states)
        case "and":
            if not isinstance(value, list) or len(value) != 2:
                raise InvalidMapFileException("'and' must have exactly two elements")
            return evaluate_formula(value[0], switch_states) and evaluate_formula(value[1], switch_states)
        case "or":
            if not isinstance(value, list) or len(value) != 2:
                raise InvalidMapFileException("'or' must have exactly two elements")
            return evaluate_formula(value[0], switch_states) or evaluate_formula(value[1], switch_states)
        case _:
            raise InvalidMapFileException(f"unknown formula key: {key!r}")
