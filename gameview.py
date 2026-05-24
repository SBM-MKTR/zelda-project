from typing import Final
import arcade
from constants import *
from textures import *
from sounds import *
from map import *
from map_parser import *
from player import *
from boomerang import *
from level import Level, build_level, grid_to_pixels

class GameView(arcade.View):
    """Main in-game view."""

    __map: Final[Map]
    world_width: Final[int]
    world_height: Final[int]
    level: Final[Level]
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
    holes: Final[arcade.SpriteList[arcade.Sprite]]
    boomerang: Final[Boomerang]
    boomerangs: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    bats: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    switches: Final[arcade.SpriteList[arcade.Sprite]]
    gates: Final[arcade.SpriteList[arcade.Sprite]]
    __gate_infos: Final[list[tuple[arcade.Sprite, GateConfig]]]
    __switch_infos: Final[list[tuple[arcade.Sprite, str]]]

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
        self.__switch_infos = self.level.switch_infos
        self.__gate_infos = self.level.gate_infos
        self._update_gates()

        self.boomerang = Boomerang()
        self.boomerangs = arcade.SpriteList(use_spatial_hash=False)
        self.boomerangs.append(self.boomerang)
        self._update_gates()

        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()
        self.camera_ui = arcade.camera.Camera2D()
        self.camera_margin_x = 40
        self.camera_margin_y = 30
        self.crystals_sound = CRYSTALS_SOUND
        self.score = 0

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

        self.camera.position = (self.player.center_x, self.player.center_y)
        self._update_camera()


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
            self.player_list.draw()
            if self.boomerang.state != BoomerangState.INACTIVE:
                self.boomerangs.draw()
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
            score_text = arcade.Text(
                f"Score: {self.score}",
                10,
                self.window.height - 30,
                arcade.color.WHITE,
                16,
            )
            score_text.draw()
            """ self.player_list.draw_hit_boxes()"""

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        if symbol == arcade.key.ESCAPE:
                self._restart()
                return
        direction = self._direction_from_key(symbol)
        if direction is not None :
            self.player.press_direction(direction)
        if symbol == arcade.key.D:
            self.boomerang.launch(self.player)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        direction = self._direction_from_key(symbol)
        if direction is not None:
            self.player.release_direction(direction)

    def _update_enemies(self) -> None:
        for enemy in self.level.enemies:
            enemy.update()

    def _update_gates(self) -> None:
        switch_states = {id: sprite.texture == TEXTURE_SWITCH_ON for sprite, id in self.__switch_infos}
        for gate_sprite, gate_config in self.__gate_infos:
            is_open = evaluate_formula(gate_config.open_if, switch_states)
            if is_open:
                gate_sprite.texture = TEXTURE_GATE_OPEN
                if gate_sprite in self.walls:
                    gate_sprite.remove_from_sprite_lists()
                    self.gates.append(gate_sprite)
            else:
                gate_sprite.texture = TEXTURE_GATE_CLOSED
                if gate_sprite not in self.walls:
                    if gate_sprite in self.gates:
                        self.gates.remove(gate_sprite)
                    self.walls.append(gate_sprite)


    def _update_camera(self) -> None:
        """Update the camera view, centered on the character but with a small margin
        for him to move freely before the camera moves. The camera also doesn't show
        the outside of the world, it stops at borders"""
        screen_w = self.window.width
        screen_h = self.window.height
        cam_x, cam_y = self.camera.position

        margin_x = self.camera_margin_x
        margin_y = self.camera_margin_y

        if self.player.center_x < cam_x - margin_x:
            cam_x = self.player.center_x + margin_x
        elif self.player.center_x > cam_x + margin_x:
            cam_x = self.player.center_x - margin_x

        if self.player.center_y < cam_y - margin_y:
            cam_y = self.player.center_y + margin_y
        elif self.player.center_y > cam_y + margin_y:
            cam_y = self.player.center_y - margin_y

        half_w = screen_w / 2
        half_h = screen_h / 2
        cam_x = max(half_w, min(cam_x, self.world_width - half_w))
        cam_y = max(half_h, min(cam_y, self.world_height - half_h))

        self.camera.position = (cam_x, cam_y)


    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()
        self._update_enemies()
        self._update_gates()

        self.player.update_animation()
        self.crystals.update_animation()
        self.spinners.update_animation()
        self.bats.update_animation()

        self.boomerang.update_boomerang(self.player)
        self.boomerang.update_animation()

        if arcade.check_for_collision_with_list(self.player, self.spinners):
            self._restart()
            return

        if arcade.check_for_collision_with_list(self.player, self.bats):
            self._restart()
            return

        for hole in self.holes:
            dx = self.player.center_x - hole.center_x
            dy = self.player.center_y - hole.center_y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= 16:
                self._restart()
                return

        for crystal in arcade.check_for_collision_with_list(self.player, self.crystals):
            crystal.remove_from_sprite_lists()
            arcade.play_sound(self.crystals_sound)
            self.score += 1

        for spinner in arcade.check_for_collision_with_list(self.boomerang, self.spinners):
            self.level.remove_enemy_sprite(spinner)
            spinner.remove_from_sprite_lists()
            if self.boomerang.state == BoomerangState.LAUNCHING:
                self.boomerang.state = BoomerangState.RETURNING

        for bat in arcade.check_for_collision_with_list(self.boomerang, self.bats):
            self.level.remove_enemy_sprite(bat)
            bat.remove_from_sprite_lists()
            if self.boomerang.state == BoomerangState.LAUNCHING:
                self.boomerang.state = BoomerangState.RETURNING

        for switch in arcade.check_for_collision_with_list(self.boomerang, self.switches):
            if switch.texture == TEXTURE_SWITCH_OFF:
                switch.texture = TEXTURE_SWITCH_ON
            elif switch.texture == TEXTURE_SWITCH_ON:
                switch.texture = TEXTURE_SWITCH_OFF
            if self.boomerang.state == BoomerangState.LAUNCHING:
                self.boomerang.state = BoomerangState.RETURNING

        if self.boomerang.state == BoomerangState.LAUNCHING:
            for wall in arcade.check_for_collision_with_list(self.boomerang, self.walls):
                self.boomerang.state = BoomerangState.RETURNING

        self._update_camera()
