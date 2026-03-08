import arcade

import sys
from pathlib import Path

from constants import *
from gameview import GameView
from map import *

DEFAULT_MAP_PATH = Path("maps") / "map1.txt"


def _get_map_path(argv: list[str]) -> Path:
    if len(argv) > 2:
        raise ValueError("Usage: uv run main.py [map_file]")
    return Path(argv[1]) if len(argv) == 2 else DEFAULT_MAP_PATH


def main() -> None:
    try:
        map_path = _get_map_path(sys.argv)
        game_map = Map.from_file(map_path)
    except ValueError as exc:
        print(exc)
        return
    except OSError:
        print(f"Impossible d'ouvrir le fichier de map : {map_path}")
        return
    except InvalidMapFileException as exc:
        print(f"Fichier de map invalide : {exc}")
        return

    window = arcade.Window(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT, WINDOW_TITLE)
    window.show_view(GameView(game_map))
    arcade.run()

if __name__ == "__main__":
    main()
