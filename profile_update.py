import cProfile
import pstats
from pathlib import Path

import arcade

from gameview import GameView
from map import Map


MAP_PATH = Path("Maps/map1.txt")
PROFILE_OUTPUT = "profile_update.prof"
WARMUP_FRAMES = 60
PROFILE_FRAMES = 600


def make_view() -> tuple[arcade.Window, GameView]:
    game_map = Map.from_file(MAP_PATH)
    window = arcade.Window(800, 600, "Profile", visible=False)
    view = GameView(game_map)
    window.show_view(view)
    return window, view


def run_updates(view: GameView, frame_count: int) -> None:
    for _ in range(frame_count):
        view.on_update(1 / 60)


def main() -> None:
    window, view = make_view()

    run_updates(view, WARMUP_FRAMES)

    profiler = cProfile.Profile()
    profiler.enable()
    run_updates(view, PROFILE_FRAMES)
    profiler.disable()

    profiler.dump_stats(PROFILE_OUTPUT)

    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumtime")
    stats.print_stats(20)

    window.close()

    print(f"Profile written to {PROFILE_OUTPUT}")


if __name__ == "__main__":
    main()
