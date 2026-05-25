from enum import Enum
from dataclasses import dataclass
from typing import Any


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
    PLAYER_START = "player_start"


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
    radius: float


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
    open_if: dict[str, Any]


@dataclass(frozen=True)
class ParsedHeader:
    width: int
    height: int
    switches_data: list
    gates_data: list
    map_start_index: int
