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
    crystals_sound: Final[arcade.Sound]

    def __init__(self, map: Map) -> None:
        # Magical incantion: initialize the Arcade view
        super().__init__()

        self.__map = map
        # Choose a nice comfy background color
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

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
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.camera = arcade.camera.Camera2D()
        self.crystals_sound = CRYSTALS_SOUND

    def on_show_view(self) -> None:
        """Called automatically by 'window.show_view(game_view)' in main.py."""
        # When we show the view, adjust the window's size to our world size.
        # If the world size is smaller than the maximum window size, we should
        # limit the size of the window.
        self.window.width = min(MAX_WINDOW_WIDTH, self.world_width)
        self.window.height = min(MAX_WINDOW_HEIGHT, self.world_height)

    def on_draw(self) -> None:
        """Render the screen."""
        self.clear() # always start with self.clear()
        with self.camera.activate():
             self.grounds.draw()
             self.walls.draw()
             self.crystals.draw()
             self.player_list.draw()
             # Hit boxes (debug)
             self.walls.draw_hit_boxes()
             self.crystals.draw_hit_boxes()
             self.player_list.draw_hit_boxes()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when the user presses a key on the keyboard."""
        match symbol:
            case arcade.key.ESCAPE:
                # redémarrer le jeu en recréant la vue
                self.window.show_view(GameView(self.__map))
            case arcade.key.RIGHT:
                # start moving to the right
                self.player.change_x = +PLAYER_MOVEMENT_SPEED
            case arcade.key.LEFT:
                # start moving to the left
                self.player.change_x = -PLAYER_MOVEMENT_SPEED
            case arcade.key.UP:
                # start moving upwards
                self.player.change_y = +PLAYER_MOVEMENT_SPEED
            case arcade.key.DOWN:
                # start moving downwards
                self.player.change_y = -PLAYER_MOVEMENT_SPEED

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the user releases a key on the keyboard."""
        match symbol:
            case arcade.key.RIGHT | arcade.key.LEFT:
                # stop horizontal movement
                self.player.change_x = 0
            case arcade.key.UP | arcade.key.DOWN:
                # stop vertical movement
                self.player.change_y = 0

    def on_update(self, delta_time: float) -> None:
        """Called once per frame, before drawing.

        This is where in-world time "advances", or "ticks".
        """
        self.physics_engine.update()
        self.player.update_animation()
        self.crystals.update_animation()
        # ramasser les cristaux en collision avec le joueur
        for crystal in arcade.check_for_collision_with_list(self.player, self.crystals):
            crystal.remove_from_sprite_lists()
            arcade.play_sound(self.crystals_sound)
        self.camera.position = self.player.position
