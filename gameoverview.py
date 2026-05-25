import arcade
from map import Map

class GameOverView(arcade.View):
    def __init__(self, game_map: Map, score: int) -> None:
        super().__init__()
        self.game_map = game_map
        self.score = score

        self.title = arcade.Text(
            "GAME OVER",
            0, 0,
            arcade.color.RED,
            50,
            anchor_x="center",
        )

        self.score_text = arcade.Text(
            f"Score: {self.score}",
            0, 0,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.restart_text = arcade.Text(
            "Press ENTER to restart",
            0, 0,
            arcade.color.GRAY,
            16,
            anchor_x="center",
        )

    def on_show_view(self) -> None:
        self.window.background_color = arcade.color.BLACK

    def on_draw(self) -> None:
        self.clear()

        center_x = self.window.width / 2
        center_y = self.window.height / 2

        self.title.position = (center_x, center_y + 50)
        self.score_text.position = (center_x, center_y)
        self.restart_text.position = (center_x, center_y - 50)

        self.title.draw()
        self.score_text.draw()
        self.restart_text.draw()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ENTER:
            from gameview import GameView
            self.window.show_view(GameView(self.game_map))
