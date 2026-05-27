import statistics
import timeit

import arcade

from gameview import GameView
from map import Map


BENCHMARK_MAP = """width: 12
height: 8
switches:
- id: sw1
  x: 8
  y: 3
  state: off
gates:
- x: 9
  y: 3
  open_if:
    switch_is_on: sw1
teleporters:
- id: tp1
  x: 6
  y: 1
  target_id: tp2
- id: tp2
  x: 10
  y: 6
  target_id: tp1
keys:
- id: key1
  x: 7
  y: 2
chests:
- id: chest1
  x: 8
  y: 2
  key_id: key1
---
xxxxxxxxxxxx
x         Tx
x     b    x
x   v      x
x P   s ^|x
x   *  kC x
x     T    x
xxxxxxxxxxxx
---
"""


def make_view() -> tuple[arcade.Window, GameView]:
    game_map = Map.from_string(BENCHMARK_MAP)
    window = arcade.Window(640, 480, "Benchmark", visible=False)
    view = GameView(game_map)
    window.show_view(view)
    return window, view


def benchmark_on_update() -> tuple[float, float]:
    number = 300

    timings = []
    for _ in range(10):
        window, view = make_view()

        elapsed = timeit.timeit(
            lambda: view.on_update(1 / 60),
            number=number,
        )

        timings.append(elapsed / number)
        window.close()

    return statistics.mean(timings), statistics.stdev(timings)


def main() -> None:
    mean, stdev = benchmark_on_update()

    print("GameView.on_update benchmark")
    print(f"mean:  {mean * 1000:.4f} ms/frame")
    print(f"stdev: {stdev * 1000:.4f} ms/frame")
    print("budget for 60 FPS: 16.6667 ms/frame")


if __name__ == "__main__":
    main()
