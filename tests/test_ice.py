import arcade

from constants import PLAYER_MOVEMENT_SPEED
from player import Direction, Player


def test_ground_player_reaches_full_speed_instantly(window: arcade.Window) -> None:
    player = Player(center_x=100, center_y=100)
    player.press_direction(Direction.EAST)
    player.update_physics(on_ice=False)
    assert player.change_x == PLAYER_MOVEMENT_SPEED


def test_ground_player_stops_immediately_on_key_release(window: arcade.Window) -> None:
    player = Player(center_x=100, center_y=100)
    player.press_direction(Direction.EAST)
    for _ in range(5):
        player.update_physics(on_ice=False)

    player.release_direction(Direction.EAST)
    player.update_physics(on_ice=False)

    assert player.change_x == 0.0


def test_ice_player_accelerates_slowly(window: arcade.Window) -> None:
    player = Player(center_x=100, center_y=100)
    player.press_direction(Direction.EAST)
    player.update_physics(on_ice=True)

    # On ice, speed after one frame must be well below full ice speed
    assert 0 < player.change_x < PLAYER_MOVEMENT_SPEED


def test_ice_player_slides_after_releasing_key(window: arcade.Window) -> None:
    player = Player(center_x=100, center_y=100)
    player.press_direction(Direction.EAST)

    for _ in range(30):
        player.update_physics(on_ice=True)

    player.release_direction(Direction.EAST)
    player.update_physics(on_ice=True)

    # On ice, the player keeps a significant velocity after releasing the key
    assert player.change_x > 0
