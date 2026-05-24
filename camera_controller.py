from dataclasses import dataclass

import arcade

from constants import CAMERA_MARGIN_X, CAMERA_MARGIN_Y
from player import Player


@dataclass
class CameraController:
    camera: arcade.camera.Camera2D
    player: Player
    world_width: int
    world_height: int
    margin_x: int = CAMERA_MARGIN_X
    margin_y: int = CAMERA_MARGIN_Y

    def center_on_player(self) -> None:
        self.camera.position = (self.player.center_x, self.player.center_y)

    def update(self, screen_width: int, screen_height: int) -> None:
        cam_x, cam_y = self.camera.position

        if self.player.center_x < cam_x - self.margin_x:
            cam_x = self.player.center_x + self.margin_x
        elif self.player.center_x > cam_x + self.margin_x:
            cam_x = self.player.center_x - self.margin_x

        if self.player.center_y < cam_y - self.margin_y:
            cam_y = self.player.center_y + self.margin_y
        elif self.player.center_y > cam_y + self.margin_y:
            cam_y = self.player.center_y - self.margin_y

        cam_x = self._clamp_camera_axis(
            camera_position=cam_x,
            screen_size=screen_width,
            world_size=self.world_width,
        )
        cam_y = self._clamp_camera_axis(
            camera_position=cam_y,
            screen_size=screen_height,
            world_size=self.world_height,
        )

        self.camera.position = (cam_x, cam_y)

    @staticmethod
    def _clamp_camera_axis(
        camera_position: float,
        screen_size: int,
        world_size: int,
    ) -> float:
        if world_size <= screen_size:
            return world_size / 2

        half_screen = screen_size / 2
        return max(half_screen, min(camera_position, world_size - half_screen))
