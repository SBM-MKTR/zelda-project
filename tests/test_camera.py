from camera_controller import CameraController
import arcade
from gameview import GameView
from map import Map
from constants import CAMERA_MARGIN_X

def test_clamp_stays_in_bounds() -> None:
    assert CameraController._clamp_camera_axis(10, 800, 1600) == 400

def test_clamp_right_edge() -> None:
        assert CameraController._clamp_camera_axis(1590, 800, 1600) == 1200

def test_clamp_small_world() -> None:
        assert CameraController._clamp_camera_axis(0, 800, 400) == 200

MAP = """width: 20
height: 20
---
xxxxxxxxxxxxxxxxxxxx
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
x        P         x
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
x                  x
xxxxxxxxxxxxxxxxxxxx
---
"""

def _make_view(window: arcade.Window) -> GameView:
    game_map = Map.from_string(MAP)
    view = GameView(game_map)
    window.show_view(view)
    return view


def test_player_within_margin_camera_does_not_move(window: arcade.Window) -> None:
    view = _make_view(window)
    cam_x_before, _ = view.camera.position
    view.player.center_x = cam_x_before + CAMERA_MARGIN_X - 1
    view.on_update(1 / 60)
    cam_x_after, _ = view.camera.position
    assert cam_x_after == cam_x_before

def test_camera_follows_player_when_outside_margin(window: arcade.Window) -> None:
    view = _make_view(window)
    cam_x_before, _ = view.camera.position
    view.player.center_x = cam_x_before + CAMERA_MARGIN_X + 10
    view.on_update(1 / 60)
    cam_x_after, _ = view.camera.position
    assert cam_x_after > cam_x_before
