from enum import Enum
from dataclasses import dataclass


class InvalidMapFileException(Exception):
    """Exception raised when a map file is malformed or does not respect structural constraints."""
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
    TELEPORTER = "teleporter"
    KEY = "key"
    CHEST = "chest"
    PLAYER_START = "player_start"
    ICE = "ice"


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
    open_if: dict


@dataclass(frozen=True)
class TeleporterConfig:
    id: str
    x: int
    y: int
    target_id: str


@dataclass(frozen=True)
class KeyConfig:
    id: str
    x: int
    y: int


@dataclass(frozen=True)
class ChestConfig:
    id: str
    x: int
    y: int
    key_id: str


@dataclass(frozen=True)
class ParsedHeader:
    """Intermediate result of parsing the YAML header: dimensions, raw entity lists,
    and the line index where the grid starts."""
    width: int
    height: int
    switches_data: list
    gates_data: list
    teleporters_data: list
    keys_data: list
    chests_data: list
    map_start_index: int
