import arcade

import sys
from pathlib import Path

from constants import *
from gameview import GameView
from map import *

DEFAULT_MAP_PATH = Path("maps") / "map1.txt"

def main() -> None:
    if len(sys.argv) == 1:
        map_path = DEFAULT_MAP_PATH
    elif len(sys.argv) == 2:
        map_path = sys.argv[1]
    else:
        print("Usage: uv run main.py [map_file]")
        return

    try:
        game_map = Map.from_file(map_path)
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
