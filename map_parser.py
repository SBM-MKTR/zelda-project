from ruamel.yaml import YAML
from ruamel.yaml.constructor import DuplicateKeyError
from ruamel.yaml.error import YAMLError

from map_types import (
    InvalidMapFileException,
    GridCell,
    SwitchConfig,
    GateConfig,
    TeleporterConfig,
    KeyConfig,
    ChestConfig,
    ParsedHeader,
)


def parse_header(lines: list[str]) -> ParsedHeader:
    if not lines:
        raise InvalidMapFileException("empty map file")

    try:
        separator_index = lines.index("---")
    except ValueError:
        raise InvalidMapFileException("missing configuration terminator '---'") from None

    yaml_text = "\n".join(lines[:separator_index])
    yaml_parser = YAML(typ="safe")
    yaml_parser.allow_duplicate_keys = False

    try:
        config = yaml_parser.load(yaml_text)
    except DuplicateKeyError as exc:
        raise InvalidMapFileException(f"duplicate YAML key in header: {exc}") from exc
    except YAMLError as exc:
        raise InvalidMapFileException(f"invalid YAML in header: {exc}") from exc

    if not isinstance(config, dict):
        raise InvalidMapFileException("configuration must be a YAML mapping")

    width = _require_positive_int(config, "width")
    height = _require_positive_int(config, "height")
    switches = _optional_list(config, "switches")
    gates = _optional_list(config, "gates")
    teleporters = _optional_list(config, "teleporters")
    keys = _optional_list(config, "keys")
    chests = _optional_list(config, "chests")

    return ParsedHeader(
        width=width,
        height=height,
        switches_data=switches,
        gates_data=gates,
        teleporters_data=teleporters,
        keys_data=keys,
        chests_data=chests,
        map_start_index=separator_index + 1,
    )


def _require_positive_int(config: dict, key: str) -> int:
    if key not in config:
        raise InvalidMapFileException(f"missing configuration key: {key!r}")

    value = config[key]

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise InvalidMapFileException(f"{key} must be a strictly positive integer")

    return value


def _optional_list(config: dict, key: str) -> list:
    value = config.get(key, [])

    if value is None:
        return []

    if not isinstance(value, list):
        raise InvalidMapFileException(f"{key!r} must be a list")

    return value


def parse_map_rows(lines: list[str], map_start_index: int, height: int) -> list[str]:
    final_terminator_index = map_start_index + height

    if len(lines) < final_terminator_index + 1:
        raise InvalidMapFileException(
            "map section does not contain the expected number of lines"
        )

    raw_map_rows = lines[map_start_index:final_terminator_index]

    if lines[final_terminator_index] != "---":
        raise InvalidMapFileException("missing final terminator '---'")

    if len(lines) != final_terminator_index + 1:
        raise InvalidMapFileException("extra content after final terminator")

    return raw_map_rows


def build_grid(
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
                    raise InvalidMapFileException("map must contain exactly one 'P'")
                player_position = (x, y)
                grid[y][x] = GridCell.PLAYER_START
                continue

            grid[y][x] = _cell_from_char(char)

    if player_position is None:
        raise InvalidMapFileException("map must contain exactly one 'P'")

    return player_position[0], player_position[1], grid


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
        case "T":
            return GridCell.TELEPORTER
        case "k":
            return GridCell.KEY
        case "C":
            return GridCell.CHEST
        case "g":
            return GridCell.ICE
        case _:
            raise InvalidMapFileException(f"invalid map character: {char!r}")


def _parse_switch_state(value: object) -> bool:
    match value:
        case None | False | "off":
            return False
        case True | "on":
            return True
        case _:
            raise InvalidMapFileException(
                f"switch state must be 'on' or 'off', got {value!r}"
            )


def parse_switches(data: list) -> tuple[SwitchConfig, ...]:
    result: list[SwitchConfig] = []
    seen_ids: set[str] = set()

    for item in data:
        match item:
            case {
                "id": str(switch_id),
                "x": int(x),
                "y": int(y),
                **rest
            } if not isinstance(x, bool) and not isinstance(y, bool):
                pass
            case _:
                raise InvalidMapFileException(
                    f"invalid switch entry: {item!r}"
                )

        if switch_id in seen_ids:
            raise InvalidMapFileException(
                f"duplicate switch id: {switch_id!r}"
                )
        seen_ids.add(switch_id)

        state = _parse_switch_state(rest.get("state"))
        result.append(SwitchConfig(id=switch_id, x=x, y=y, state=state))

    return tuple(result)

def parse_gates(data: list) -> tuple[GateConfig, ...]:
    result: list[GateConfig] = []

    for item in data:
        match item:
            case {
                "x": int(x),
                "y": int(y),
                "open_if": dict(open_if),
                **_rest
            } if not isinstance(x, bool) and not isinstance(y, bool):
                pass
            case _:
                raise InvalidMapFileException(
                    f"invalid gate entry: {item!r}"
                    )

        result.append(GateConfig(x=x, y=y, open_if=open_if))

    return tuple(result)

def parse_teleporters(data: list) -> tuple[TeleporterConfig, ...]:
    result: list[TeleporterConfig] = []
    seen_ids: set[str] = set()

    for item in data:
        match item:
            case {
                "id": str(tp_id),
                "x": int(x),
                "y": int(y),
                "target_id": str(target_id),
            } if not isinstance(x, bool) and not isinstance(y, bool):
                pass
            case _:
                raise InvalidMapFileException(
                    f"invalid teleporter entry: {item!r}"
                )

        if tp_id in seen_ids:
            raise InvalidMapFileException(f"duplicate teleporter id: {tp_id!r}")
        seen_ids.add(tp_id)

        result.append(TeleporterConfig(id=tp_id, x=x, y=y, target_id=target_id))

    for tc in result:
        if tc.target_id not in seen_ids:
            raise InvalidMapFileException(
                f"teleporter {tc.id!r} references unknown target_id: {tc.target_id!r}"
            )

    return tuple(result)


def parse_keys(data: list) -> tuple[KeyConfig, ...]:
    result: list[KeyConfig] = []
    seen_ids: set[str] = set()

    for item in data:
        match item:
            case {
                "id": str(key_id),
                "x": int(x),
                "y": int(y),
            } if not isinstance(x, bool) and not isinstance(y, bool):
                pass
            case _:
                raise InvalidMapFileException(f"invalid key entry: {item!r}")

        if key_id in seen_ids:
            raise InvalidMapFileException(f"duplicate key id: {key_id!r}")
        seen_ids.add(key_id)

        result.append(KeyConfig(id=key_id, x=x, y=y))

    return tuple(result)


def parse_chests(data: list, known_key_ids: set[str]) -> tuple[ChestConfig, ...]:
    result: list[ChestConfig] = []
    seen_ids: set[str] = set()

    for item in data:
        match item:
            case {
                "id": str(chest_id),
                "x": int(x),
                "y": int(y),
                "key_id": str(key_id),
            } if not isinstance(x, bool) and not isinstance(y, bool):
                pass
            case _:
                raise InvalidMapFileException(f"invalid chest entry: {item!r}")

        if chest_id in seen_ids:
            raise InvalidMapFileException(f"duplicate chest id: {chest_id!r}")
        seen_ids.add(chest_id)

        if key_id not in known_key_ids:
            raise InvalidMapFileException(
                f"chest {chest_id!r} references unknown key id: {key_id!r}"
            )

        result.append(ChestConfig(id=chest_id, x=x, y=y, key_id=key_id))

    return tuple(result)


def validate_formula(formula: object, known_ids: set[str], _depth: int = 0) -> None:
    """Valide récursivement la structure complète d'une formule logique au chargement.

    Vérifie : type dict, clé unique, opérateur connu, nombre exact d'opérandes,
    ids de switches existants, et profondeur maximale.
    """
    if _depth > 10:
        raise InvalidMapFileException("formula nesting exceeds maximum depth (10)")

    if not isinstance(formula, dict) or len(formula) != 1:
        raise InvalidMapFileException(
            f"a formula must be a dict with exactly one key, got: {formula!r}"
        )

    match formula:
        case {"switch_is_on": str(switch_id)}:
            if switch_id not in known_ids:
                raise InvalidMapFileException(
                    f"gate condition references unknown switch id: {switch_id!r}"
                )

        case {"switch_is_on": bad}:
            raise InvalidMapFileException(
                f"switch_is_on value must be a string, got: {bad!r}"
            )

        case {"not": [operand]}:
            validate_formula(operand, known_ids, _depth + 1)

        case {"not": bad}:
            raise InvalidMapFileException(
                f"'not' must have exactly one operand, got: {bad!r}"
            )

        case {"and": [left, right]}:
            validate_formula(left, known_ids, _depth + 1)
            validate_formula(right, known_ids, _depth + 1)

        case {"and": bad}:
            raise InvalidMapFileException(
                f"'and' must have exactly two operands, got: {bad!r}"
            )

        case {"or": [left, right]}:
            validate_formula(left, known_ids, _depth + 1)
            validate_formula(right, known_ids, _depth + 1)

        case {"or": bad}:
            raise InvalidMapFileException(
                f"'or' must have exactly two operands, got: {bad!r}"
            )

        case {**unknown}:
            key = next(iter(unknown))
            raise InvalidMapFileException(f"unknown formula operator: {key!r}")


def evaluate_formula(
    formula: object, switch_states: dict[str, bool], _depth: int = 0
) -> bool:
    if _depth > 10:
        raise InvalidMapFileException("formula nesting exceeds maximum depth (10)")
    match formula:
        case {"switch_is_on": str(switch_id)}:
            return switch_states[switch_id]
        case {"not": [operand]}:
            return not evaluate_formula(operand, switch_states, _depth + 1)
        case {"and": [left, right]}:
            return (
                evaluate_formula(left, switch_states, _depth + 1)
                and evaluate_formula(right, switch_states, _depth + 1)
            )
        case {"or": [left, right]}:
            return (
                evaluate_formula(left, switch_states, _depth + 1)
                or evaluate_formula(right, switch_states, _depth + 1)
            )
        case _:
            raise InvalidMapFileException(f"invalid formula: {formula!r}")
