from typing import Final

import arcade

from camera_controller import CameraController
from collision_system import CollisionSystem
from constants import (
    MAX_WINDOW_HEIGHT,
    MAX_WINDOW_WIDTH,
    SCORE_TEXT_SIZE,
    SCORE_TEXT_TOP_MARGIN,
    SCORE_TEXT_X,
)
from gate_system import GateSystem
from level import Level, build_level, grid_to_pixels
from map import Map
from player import Direction, Player
from boomerang import Boomerang
from weapon_system import WeaponSystem
from sounds import CRYSTALS_SOUND

class GameView(arcade.View):
    """Main in-game view."""

    __map: Final[Map]
    world_width: Final[int]
    world_height: Final[int]
    level: Final[Level]
    gate_system: Final[GateSystem]
    player: Final[Player]
    player_list: Final[arcade.SpriteList[Player]]
    grounds: Final[arcade.SpriteList[arcade.Sprite]]
    walls: Final[arcade.SpriteList[arcade.Sprite]]
    crystals: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]
    camera_ui: Final[arcade.camera.Camera2D]
    crystals_sound: Final[arcade.Sound]
    spinners: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    score: int
    score_text: Final[arcade.Text]
    holes: Final[arcade.SpriteList[arcade.Sprite]]
    boomerang: Final[Boomerang]
    bats: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    switches: Final[arcade.SpriteList[arcade.Sprite]]
    gates: Final[arcade.SpriteList[arcade.Sprite]]
    collision_system: Final[CollisionSystem]
    camera_controller: Final[CameraController]
    weapon_system: Final[WeaponSystem]

    def __init__(self, map: Map) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        self.__map = map

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        self.level = build_level(map)
        self.world_width = self.level.world_width
        self.world_height = self.level.world_height

        self.player = Player(
            center_x=grid_to_pixels(map.player_start_x),
            center_y=grid_to_pixels(map.player_start_y),
        )

        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)

        self.grounds = self.level.grounds
        self.walls = self.level.walls
        self.crystals = self.level.crystals
        self.spinners = self.level.spinners
        self.holes = self.level.holes
        self.bats = self.level.bats
        self.switches = self.level.switches
        self.gates = self.level.gates
        self.gate_system = GateSystem(
            switch_infos=self.level.switch_infos,
            gate_infos=self.level.gate_infos,
            walls=self.walls,
            gates=self.gates,
        )
        self.gate_system.update()
        self.weapon_system = WeaponSystem()
        self.boomerang = self.weapon_system.boomerang_weapon.boomerang

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()
        self.camera_ui = arcade.camera.Camera2D()
        self.camera_controller = CameraController(
            camera=self.camera,
            player=self.player,
            world_width=self.world_width,
            world_height=self.world_height,
        )
        self.crystals_sound = CRYSTALS_SOUND
        self.collision_system = CollisionSystem(
            level=self.level,
            player=self.player,
            weapon_system=self.weapon_system,
            gate_system=self.gate_system,
            crystals_sound=self.crystals_sound,
        )
        self.score = 0
        self.score_text = arcade.Text(
            "Score: 0",
            SCORE_TEXT_X,
            self.window.height - SCORE_TEXT_TOP_MARGIN,
            arcade.color.WHITE,
            SCORE_TEXT_SIZE,
        )

    def _restart(self) -> None:
        """Réinitialise le jeu en créant une nouvelle instance de GameView"""
        self.window.show_view(GameView(self.__map))

    @staticmethod
    def _direction_from_key(symbol: int) -> Direction | None:
        match symbol:
            case arcade.key.RIGHT:
                return Direction.EAST
            case arcade.key.LEFT:
                return Direction.WEST
            case arcade.key.UP:
                return Direction.NORTH
            case arcade.key.DOWN:
                return Direction.SOUTH
            case _:
                return None

    def on_show_view(self) -> None:
        """Called automatically by 'window.show_view(game_view)' in main.py."""
        # When we show the view, adjust the window's size to our world size.
        # If the world size is smaller than the maximum window size, we should
        # limit the size of the window.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)
        self.score_text.y = self.window.height - SCORE_TEXT_TOP_MARGIN

        self.camera_controller.center_on_player()
        self.camera_controller.update(self.window.width, self.window.height)

    def on_draw(self) -> None:
        """Draw all game elements.
        Renders two layers using separate cameras:
        - World camera: ground, holes, walls, crystals, spinners, player, boomerang and bats
        - UI camera: score display (fixed to screen, independent of world movement)
        """
        self.clear() # always start with self.clear()
        with self.camera.activate():
            self.grounds.draw()
            self.holes.draw()
            self.walls.draw()
            self.crystals.draw()
            self.spinners.draw()
            self.switches.draw()
            self.gates.draw()
            if not self.weapon_system.sword_weapon.is_active():
                self.player_list.draw()
            self.weapon_system.draw()
            self.bats.draw()
            # Hit boxes (debug)
            '''self.walls.draw_hit_boxes()
            self.crystals.draw_hit_boxes()
            self.spinners.draw_hit_boxes()
            self.player_list.draw_hit_boxes()
            self.holes.draw_hit_boxes()
            self.bats.draw_hit_boxes()
            self.switches.draw_hit_boxes()
            self.gates.draw_hit_boxes'''

        with self.camera_ui.activate():
            self.weapon_system.draw_active_weapon_icon(self.window.height)
            self.score_text.text = f"Score: {self.score}"
            self.score_text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.ESCAPE:
                self._restart()

            case arcade.key.R:
                self.weapon_system.switch_active_weapon()

            case arcade.key.D:
                self.weapon_system.use_active_weapon(self.player)

            case _:
                direction = self._direction_from_key(symbol)

                if direction is not None and not self.weapon_system.sword_weapon.is_active():
                    self.player.press_direction(direction)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        direction = self._direction_from_key(symbol)
        if direction is not None:
            self.player.release_direction(direction)

    def _update_enemies(self) -> None:
        for enemy in self.level.enemies:
            enemy.update()

    def _update_gates(self) -> None:
        self.gate_system.update()

    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        if not self.weapon_system.sword_weapon.is_active():
            self.physics_engine.update()
        self._update_enemies()
        self._update_gates()

        self.player.update_animation()
        self.crystals.update_animation()
        self.spinners.update_animation()
        self.bats.update_animation()

        self.weapon_system.update(self.player, delta_time)

        collision_result = self.collision_system.update()

        if collision_result.should_restart:
            self._restart()
            return

        self.score += collision_result.score_delta

        self.camera_controller.update(self.window.width, self.window.height)
