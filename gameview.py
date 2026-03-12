from typing import Final
import arcade

from constants import *
from textures import *
from sounds import *
from map import *

def grid_to_pixels(i : int) ->int:
    return i * TILE_SIZE + (TILE_SIZE // 2)

class GameView(arcade.View):
    """Main in-game view."""

    __map: Final[Map]
    world_width: Final[int]
    world_height: Final[int]
    player: Final[arcade.TextureAnimationSprite]
    player_list: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    grounds: Final[arcade.SpriteList[arcade.Sprite]]
    walls: Final[arcade.SpriteList[arcade.Sprite]]
    crystals: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    physics_engine: Final[arcade.PhysicsEngineSimple]
    camera: Final[arcade.camera.Camera2D]
    camera_ui: Final[arcade.camera.Camera2D]
    crystals_sound: Final[arcade.Sound]
    spinners: Final[arcade.SpriteList[arcade.TextureAnimationSprite]]
    __spinner_infos: Final[list[tuple[arcade.TextureAnimationSprite, int, int, int, int]]]
    score: int

    def __init__(self, map: Map) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        self.__map = map

        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Keyboard state
        self.right_pressed = False
        self.left_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Setup our game
        self.world_width = map.width * TILE_SIZE
        self.world_height = map.height * TILE_SIZE
        self.player = arcade.TextureAnimationSprite(
            animation=ANIMATION_PLAYER_IDLE_DOWN,
            scale=SCALE, center_x=grid_to_pixels(map.player_start_x), center_y=grid_to_pixels(map.player_start_y)
        )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.grounds = arcade.SpriteList(use_spatial_hash=True)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.crystals = arcade.SpriteList(use_spatial_hash=True)
        self.spinners = arcade.SpriteList(use_spatial_hash=False)
        self.__spinner_infos: list[
            tuple[arcade.TextureAnimationSprite, int, int, int, int]
        ] = []
        for y in range(map.height):
            for x in range(map.width):
                grass = arcade.Sprite(
                    TEXTURE_GRASS,
                    scale=SCALE,
                    center_x=grid_to_pixels(x),
                    center_y=grid_to_pixels(y),
                )
                self.grounds.append(grass)

                cell = map.get(x, y)
                if cell == GridCell.BUSH:
                    bush = arcade.Sprite(
                        TEXTURE_BUSH,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )
                    self.walls.append(bush)
                elif cell == GridCell.CRYSTAL:
                    crystal = arcade.TextureAnimationSprite(
                        animation=ANIMATION_CRYSTAL,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )
                    self.crystals.append(crystal)
                elif cell in (GridCell.SPINNER_HORIZONTAL, GridCell.SPINNER_VERTICAL):
                    spinner = arcade.TextureAnimationSprite(
                        animation=ANIMATION_SPINNERS,
                        scale=SCALE,
                        center_x=grid_to_pixels(x),
                        center_y=grid_to_pixels(y),
                    )

                    bounds = spinner_bounds(map, x, y)
                    min_x_pixels = grid_to_pixels(bounds.min_x)
                    max_x_pixels = grid_to_pixels(bounds.max_x)
                    min_y_pixels = grid_to_pixels(bounds.min_y)
                    max_y_pixels = grid_to_pixels(bounds.max_y)

                    if cell == GridCell.SPINNER_HORIZONTAL:
                        if min_x_pixels != max_x_pixels:
                            spinner.change_x = SPINNER_MOVEMENT_SPEED
                    else:
                        if min_y_pixels != max_y_pixels:
                            spinner.change_y = SPINNER_MOVEMENT_SPEED

                    self.spinners.append(spinner)
                    self.__spinner_infos.append(
                        (
                            spinner,
                            min_x_pixels,
                            max_x_pixels,
                            min_y_pixels,
                            max_y_pixels,
                        )
                    )
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()
        self.camera_ui = arcade.camera.Camera2D()
        self.camera_margin_x = 40
        self.camera_margin_y = 30
        self.crystals_sound = CRYSTALS_SOUND
        self.score = 0

    def _restart(self) -> None:
        self.window.show_view(GameView(self.__map))

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
        """Render the screen."""
        self.clear() # always start with self.clear()
        with self.camera.activate():
            self.grounds.draw()
            self.walls.draw()
            self.crystals.draw()
            self.spinners.draw()
            self.player_list.draw()
            # Hit boxes (debug)
            self.walls.draw_hit_boxes()
            self.crystals.draw_hit_boxes()
            self.spinners.draw_hit_boxes()
            self.player_list.draw_hit_boxes()

        with self.camera_ui.activate():
            score_text = arcade.Text(
                f"Score: {self.score}",
                10,
                self.window.height - 30,
                arcade.color.WHITE,
                16,
            )
            score_text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match symbol:
            case arcade.key.ESCAPE:
                self._restart()
            case arcade.key.RIGHT:
                # start moving to the right
                self.right_pressed = True
                self.player.change_x = +PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.left_pressed = True
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                # start moving upwards
                self.up_pressed = True
                self.player.change_y = +PLAYER_MOVEMENT_SPEED
            case arcade.key.DOWN:
                # start moving downwards
                self.down_pressed = True
                self.player.change_y = -PLAYER_MOVEMENT_SPEED

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match symbol:
            case arcade.key.RIGHT:
                self.right_pressed = False
            case arcade.key.LEFT:
                self.left_pressed = False
            case arcade.key.UP:
                self.up_pressed = False
            case arcade.key.DOWN:
                self.down_pressed = False

        # Update horizontal movement
        if self.right_pressed and not self.left_pressed:
            self.player.change_x = +PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player.change_x = 0

        # Update vertical movement
        if self.up_pressed and not self.down_pressed:
            self.player.change_y = +PLAYER_MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player.change_y = -PLAYER_MOVEMENT_SPEED
        else:
            self.player.change_y = 0

    def _update_spinners(self) -> None:
        for spinner, min_x_pixels, max_x_pixels, min_y_pixels, max_y_pixels in self.__spinner_infos:
            spinner.center_x += spinner.change_x
            spinner.center_y += spinner.change_y

            if spinner.change_x > 0 and spinner.center_x >= max_x_pixels:
                spinner.center_x = max_x_pixels
                spinner.change_x = -SPINNER_MOVEMENT_SPEED

            elif spinner.change_x < 0 and spinner.center_x <= min_x_pixels:
                spinner.center_x = min_x_pixels
                spinner.change_x = SPINNER_MOVEMENT_SPEED

            elif spinner.change_y > 0 and spinner.center_y >= max_y_pixels:
                spinner.center_y = max_y_pixels
                spinner.change_y = -SPINNER_MOVEMENT_SPEED

            elif spinner.change_y < 0 and spinner.center_y <= min_y_pixels:
                spinner.center_y = min_y_pixels
                spinner.change_y = SPINNER_MOVEMENT_SPEED

    def _update_camera(self) -> None:
        screen_w = self.window.width
        screen_h = self.window.height
        cam_x, cam_y = self.camera.position

        # Marges (zone où le joueur peut bouger sans déplacer la caméra)
        margin_x = self.camera_margin_x
        margin_y = self.camera_margin_y

        # Déplacer horizontalement
        if self.player.center_x < cam_x - margin_x:
            cam_x = self.player.center_x + margin_x
        elif self.player.center_x > cam_x + margin_x:
            cam_x = self.player.center_x - margin_x

        # Déplacer verticalement
        if self.player.center_y < cam_y - margin_y:
            cam_y = self.player.center_y + margin_y
        elif self.player.center_y > cam_y + margin_y:
            cam_y = self.player.center_y - margin_y

        # Limiter la caméra pour ne jamais montrer l’extérieur du monde
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
        self._update_spinners()

        self.player.update_animation()
        self.crystals.update_animation()
        self.spinners.update_animation()

        if arcade.check_for_collision_with_list(self.player, self.spinners):
            self._restart()
            return

        # ramasser les cristaux en collision avec le joueur
        for crystal in arcade.check_for_collision_with_list(self.player, self.crystals):
            crystal.remove_from_sprite_lists()
            arcade.play_sound(self.crystals_sound)
            self.score += 1

        self._update_camera()
