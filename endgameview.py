import arcade
from map import Map
from typing import Final


class EndGameView(arcade.View):
    game_map: Final[Map]
    score: Final[int]
    title: arcade.Text
    score_text: Final[arcade.Text]
    restart_text: Final[arcade.Text]
    backgroud_color_value: arcade.types.Color

    def __init__(self, game_map: Map, score: int) -> None:
        super().__init__()

        self.game_map = game_map
        self.score = score

        self.title = arcade.Text(
            "",
            0,
            0,
            arcade.color.WHITE,
            50,
            anchor_x="center",
        )

        self.score_text = arcade.Text(
            f"Score: {self.score}",
            0,
            0,
            arcade.color.WHITE,
            20,
            anchor_x="center",
        )

        self.restart_text = arcade.Text(
            "Press ENTER to start a new game !",
            0,
            0,
            arcade.color.DARK_GRAY,
            16,
            anchor_x="center",
        )

        self.background_color_value = arcade.color.BLACK

    def on_show_view(self) -> None:
        self.window.background_color = self.background_color_value

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


class GameOverView(EndGameView):
    def __init__(self, game_map: Map, score: int) -> None:
        super().__init__(game_map, score)

        self.title.text = "GAME OVER"
        self.title.color = arcade.color.RED

class GameWinView(EndGameView):
    def __init__(self, game_map: Map, score: int) -> None:
        super().__init__(game_map, score)

        self.title.text = "YOU WON!"
        self.title.color = arcade.color.BLEU_DE_FRANCE

        self.background_color_value = arcade.color.YELLOW_ROSE
