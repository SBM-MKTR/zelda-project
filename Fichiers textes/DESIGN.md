# Fichier design
```mermaid
classDiagram

%% ─────────────────────────────
%% POINT D'ENTRÉE
%% ─────────────────────────────

class Main {
    <<module>>
    +DEFAULT_MAP_PATH : str
    +main() None
}
Main --> Map : charge
Main --> GameView : lance

%% ─────────────────────────────
%% VUES
%% ─────────────────────────────

class GameView {
    -__map : Map
    -level : Level
    -world_width : int
    -world_height : int
    -player : Player
    -player_list : SpriteList
    -grounds : SpriteList
    -walls : SpriteList
    -ices : SpriteList
    -crystals : SpriteList
    -spinners : SpriteList
    -holes : SpriteList
    -bats : SpriteList
    -blobs : SpriteList
    -switches : SpriteList
    -gates : SpriteList
    -teleporters : SpriteList
    -keys : SpriteList
    -chests : SpriteList
    -weapon_system : WeaponSystem
    -gate_system : GateSystem
    -collision_system : CollisionSystem
    -power_system : PowerSystem
    -camera_controller : CameraController
    -physics_engine : PhysicsEngineSimple
    -camera : Camera2D
    -camera_ui : Camera2D
    -score : int
    -score_text : Text
    -power_text : Text
    -chest_message_text : Text
    -_chest_message_timer : int
    +on_show_view() None
    +on_draw() None
    +on_update(delta_time: float) None
    +on_key_press(symbol: int, modifiers: int) None
    +on_key_release(symbol: int, modifiers: int) None
    -_restart() None
    -_direction_from_key(symbol: int) Direction
    -_update_enemies() None
    -_update_gates() None
}

class GameOverView {
    -game_map : Map
    -score : int
    -title : Text
    -score_text : Text
    -restart_text : Text
    +on_show_view() None
    +on_draw() None
    +on_key_press(symbol: int, modifiers: int) None
}

class GameWinView {
    -game_map : Map
    -score : int
    -title : Text
    -score_text : Text
    -restart_text : Text
    +on_show_view() None
    +on_draw() None
    +on_key_press(symbol: int, modifiers: int) None
}

GameView --> GameOverView
GameView --> GameWinView
GameOverView --> GameView
GameWinView --> GameView
%% ─────────────────────────────
%% JOUEUR
%% ─────────────────────────────

class Direction {
    <<enumeration>>
    NORTH
    SOUTH
    EAST
    WEST
}

class Player {
    +direction : Direction
    -__right_pressed : bool
    -__left_pressed : bool
    -__up_pressed : bool
    -__down_pressed : bool
    -__vel_x : float
    -__vel_y : float
    +press_direction(direction: Direction) None
    +release_direction(direction: Direction) None
    +update_physics(on_ice: bool) None
    -__target_velocity(max_speed: float) tuple
    -__set_direction_pressed(direction: Direction, is_pressed: bool) None
    -__update_direction_and_animation() None
}

Player --> Direction

%% ─────────────────────────────
%% MAP, TYPES, PARSING
%% ─────────────────────────────

class GridCell {
    <<enumeration>>
    GRASS
    BUSH
    CRYSTAL
    SPINNER_HORIZONTAL
    SPINNER_VERTICAL
    HOLE
    BAT
    BLOB
    SWITCH
    GATE
    TELEPORTER
    KEY
    CHEST
    ICE
    PLAYER_START
}

class InvalidMapFileException {
    <<exception>>
}

class SpinnerBounds {
    <<dataclass>>
    +min_x : int
    +max_x : int
    +min_y : int
    +max_y : int
}

class BatBounds {
    <<dataclass>>
    +center_x : float
    +center_y : float
    +radius : float
}

class SwitchConfig {
    <<dataclass>>
    +id : str
    +x : int
    +y : int
    +state : bool
}

class GateConfig {
    <<dataclass>>
    +x : int
    +y : int
    +open_if : dict
}

class TeleporterConfig {
    <<dataclass>>
    +id : str
    +x : int
    +y : int
    +target_id : str
}

class KeyConfig {
    <<dataclass>>
    +id : str
    +x : int
    +y : int
}

class ChestConfig {
    <<dataclass>>
    +id : str
    +x : int
    +y : int
    +key_id : str
}

class ParsedHeader {
    <<dataclass>>
    +width : int
    +height : int
    +switches_data : list
    +gates_data : list
    +teleporters_data : list
    +keys_data : list
    +chests_data : list
    +map_start_index : int
}

class MapParser {
    <<module>>
    +parse_header(lines: list) ParsedHeader
    -_require_positive_int(config: dict, key: str) int
    -_optional_list(config: dict, key: str) list
    +parse_map_rows(lines: list, map_start_index: int, height: int) list
    +build_grid(rows: list, width: int, height: int) tuple
    -_cell_from_char(char: str) GridCell
    -_parse_switch_state(value: object) bool
    +parse_switches(data: list) tuple
    +parse_gates(data: list) tuple
    +parse_teleporters(data: list) tuple
    +parse_keys(data: list) tuple
    +parse_chests(data: list, known_key_ids: set) tuple
    +validate_formula(formula: object, known_ids: set, depth: int) None
    +evaluate_formula(formula: object, switch_states: dict, depth: int) bool
}

class Map {
    -__width : int
    -__height : int
    -__player_start_x : int
    -__player_start_y : int
    -__grid : tuple
    -__switch_configs : tuple
    -__gate_configs : tuple
    -__teleporter_configs : tuple
    -__key_configs : tuple
    -__chest_configs : tuple
    +width : int
    +height : int
    +player_start_x : int
    +player_start_y : int
    +switch_configs : tuple
    +gate_configs : tuple
    +teleporter_configs : tuple
    +key_configs : tuple
    +chest_configs : tuple
    +get(x: int, y: int) GridCell
    +from_file(path: str) Map
    +from_string(text: str) Map
    -_validate_entity_positions() None
}

class MapHelpers {
    <<module>>
    +spinner_bounds(game_map: Map, x: int, y: int) SpinnerBounds
    +bat_bounds(game_map: Map, x: int, y: int, radius: float) BatBounds
}

MapParser --> ParsedHeader
MapParser --> GridCell
MapParser --> SwitchConfig
MapParser --> GateConfig
MapParser --> TeleporterConfig
MapParser --> KeyConfig
MapParser --> ChestConfig
MapParser --> InvalidMapFileException

Map --> GridCell
Map --> SwitchConfig
Map --> GateConfig
Map --> TeleporterConfig
Map --> KeyConfig
Map --> ChestConfig
Map --> InvalidMapFileException
Map ..> MapParser : parse et valide
MapHelpers --> Map
MapHelpers --> SpinnerBounds
MapHelpers --> BatBounds

%% ─────────────────────────────
%% LEVEL / CONSTRUCTION DU MONDE
%% ─────────────────────────────

class LevelModule {
    <<module>>
    +grid_to_pixels(i: int) int
    +build_level(game_map: Map) Level
}

class Level {
    <<dataclass>>
    +world_width : int
    +world_height : int
    +grounds : SpriteList
    +walls : SpriteList
    +ices : SpriteList
    +crystals : SpriteList
    +spinners : SpriteList
    +holes : SpriteList
    +bats : SpriteList
    +blobs : SpriteList
    +switches : SpriteList
    +gates : SpriteList
    +teleporters : SpriteList
    +keys : SpriteList
    +chests : SpriteList
    +enemies : list~Enemy~
    +enemy_sprites : SpriteList
    +switch_infos : list
    +gate_infos : list
    +teleporter_infos : list
    +key_infos : list
    +chest_infos : list
    +remove_enemy_sprite(sprite: TextureAnimationSprite) None
}

class SwitchInfo {
    <<type alias>>
    Sprite + switch_id
}

class GateInfo {
    <<type alias>>
    Sprite + GateConfig
}

class TeleporterInfo {
    <<type alias>>
    Sprite + TeleporterConfig
}

class KeyInfo {
    <<type alias>>
    TextureAnimationSprite + KeyConfig
}

class ChestInfo {
    <<type alias>>
    TextureAnimationSprite + ChestConfig
}

LevelModule --> Map
LevelModule --> Level
LevelModule --> Textures
LevelModule --> Constants
LevelModule --> NavMesh
LevelModule --> BlobEnemy
LevelModule --> SpinnerEnemy
LevelModule --> BatEnemy

Level --> Enemy
Level --> SwitchInfo
Level --> GateInfo
Level --> TeleporterInfo
Level --> KeyInfo
Level --> ChestInfo

%% ─────────────────────────────
%% ENNEMIS
%% ─────────────────────────────

class EnemyUpdateContext {
    <<dataclass>>
    +player : Player
    +line_of_sight_walls : SpriteList
    +is_ghost_active : bool
}

class Enemy {
    <<abstract>>
    +sprite : TextureAnimationSprite
    +update(context: EnemyUpdateContext) None*
}

class SpinnerEnemy {
    <<dataclass>>
    +sprite : TextureAnimationSprite
    +min_x : int
    +max_x : int
    +min_y : int
    +max_y : int
    +from_bounds(sprite, min_x, max_x, min_y, max_y, is_horizontal) SpinnerEnemy
    +update(context: EnemyUpdateContext) None
}

class BatEnemy {
    <<dataclass>>
    +sprite : TextureAnimationSprite
    +bounds : BatBounds
    +rng : Random
    +frame_count : int
    +__post_init__() None
    +update(context: EnemyUpdateContext) None
    -_choose_random_direction() None
    -_set_direction(angle: float) None
}

class BlobEnemy {
    <<dataclass>>
    +sprite : TextureAnimationSprite
    +navmesh : Graph
    +navmesh_subdivisions : int
    +possible_destinations : list
    +rng : Random
    +destination : Position
    +path : Path
    +__post_init__() None
    +update(context: EnemyUpdateContext) None
    -_position() Position
    -_pick_new_destination() Position
    -_has_arrived() bool
    -_visible_player_position(context) Position
    -_refresh_path() None
    -_advance_along_path() None
}

class BlobModule {
    <<module>>
    +Position : type alias
    +Path : type alias
    +BLOB_DESTINATION_OBSTACLES : tuple
    -_cell_center(cell_x: int, cell_y: int) Position
    +build_possible_destinations(game_map: Map, cell_x: int, cell_y: int) list
}

Enemy <|-- SpinnerEnemy
Enemy <|-- BatEnemy
Enemy <|-- BlobEnemy
Enemy --> EnemyUpdateContext
EnemyUpdateContext --> Player
SpinnerEnemy --> BatBounds
BlobEnemy --> NavMesh
BlobModule --> BlobEnemy
BlobModule --> Map
BlobModule --> GridCell

%% ─────────────────────────────
%% NAVMESH / PATHFINDING
%% ─────────────────────────────

class NavMesh {
    <<module>>
    +NodeType : type alias
    -_is_obstacle_for_blob(cell: GridCell) bool
    -_node_pixel_position(ix: int, iy: int, n: int) tuple
    +build_navmesh(game_map: Map, n: int) Graph
    +nearest_node(graph: Graph, px: float, py: float, n: int) NodeType
    +find_path(graph: Graph, src_px: float, src_py: float, dst_px: float, dst_py: float, n: int) list
}

NavMesh --> Map
NavMesh --> GridCell

%% ─────────────────────────────
%% ARMES
%% ─────────────────────────────

class Weapon {
    <<abstract>>
    +use(player: Player) None*
    +update(player: Player, delta_time: float) None*
    +draw() None*
    +is_active() bool*
    +check_collisions(sprite_list: SpriteList) list*
    +on_hit() None*
    +can_hit_enemies() bool
    +can_toggle_switches() bool
    +can_collect_crystals() bool
    +can_hit_obstacles() bool
}

class ActiveWeapon {
    <<enumeration>>
    BOOMERANG
    SWORD
}

class BoomerangState {
    <<enumeration>>
    INACTIVE
    LAUNCHING
    RETURNING
}

class Boomerang {
    +state : BoomerangState
    +start_x : float
    +start_y : float
    +dir_x : float
    +dir_y : float
    +launch(player: Player) None
    +update_boomerang(player: Player) None
    +update_animation(delta_time: float) None
}

class BoomerangWeapon {
    +boomerang : Boomerang
    +sprites : SpriteList
    +hit_sprite_ids : set
    +use(player: Player) None
    +update(player: Player, delta_time: float) None
    +draw() None
    +is_active() bool
    +is_launching() bool
    +check_collisions(sprite_list: SpriteList) list
    +on_hit() None
    +can_toggle_switches() bool
    +can_hit_obstacles() bool
}

class SwordWeapon {
    +sprite : TextureAnimationSprite
    +hitbox : Sprite
    +elapsed_time : float
    +active : bool
    +hit_sprite_ids : set
    +use(player: Player) None
    +update(player: Player, delta_time: float) None
    +draw() None
    +is_active() bool
    +check_collisions(sprite_list: SpriteList) list
    +on_hit() None
    +can_toggle_switches() bool
    +can_collect_crystals() bool
    -_animation_for_direction(direction: Direction) TextureAnimation
    -_place_hitbox(player: Player) None
}

class WeaponSystem {
    +boomerang_weapon : BoomerangWeapon
    +sword_weapon : SwordWeapon
    +weapons : tuple~Weapon~
    +active_weapon : ActiveWeapon
    +active_weapon_icon : Sprite
    +switch_active_weapon() None
    +use_active_weapon(player: Player) None
    +launch_boomerang(player: Player) None
    +update(player: Player, delta_time: float) None
    +draw() None
    +draw_active_weapon_icon(window_height: int) None
    +has_active_weapon() bool
    +check_enemy_collisions(sprite_list: SpriteList) list
    +check_switch_collisions(sprite_list: SpriteList) list
    +check_crystal_collisions(sprite_list: SpriteList) list
    +check_obstacle_collisions(sprite_list: SpriteList) list
    -_check_collisions(sprite_list: SpriteList, predicate: Callable) list
    -_active_weapon() Weapon
    -_active_weapon_icon_texture() Texture
}

Weapon <|-- BoomerangWeapon
Weapon <|-- SwordWeapon
BoomerangWeapon --> Boomerang
Boomerang --> BoomerangState
SwordWeapon --> Direction
WeaponSystem --> ActiveWeapon
WeaponSystem --> BoomerangWeapon
WeaponSystem --> SwordWeapon
WeaponSystem --> Weapon
WeaponSystem --> Player

%% ─────────────────────────────
%% POUVOIRS
%% ─────────────────────────────

class Power {
    <<abstract>>
    +name : str*
    +on_activate(player: Player, enemies: list) None*
    +on_deactivate(player: Player, enemies: list) None*
}

class GhostPower {
    +name : str
    +on_activate(player: Player, enemies: list) None
    +on_deactivate(player: Player, enemies: list) None
}

class FreezePower {
    +name : str
    +on_activate(player: Player, enemies: list) None
    +on_deactivate(player: Player, enemies: list) None
}

class PowerSystem {
    +player : Player
    +enemies : list~Enemy~
    -_active_power : Power
    -_remaining_frames : int
    +activate_random_power() None
    +update() None
    +is_ghost_active : bool
    +is_frozen_active : bool
    +active_power_name : str
    +remaining_frames : int
}

Power <|-- GhostPower
Power <|-- FreezePower
PowerSystem --> Power
PowerSystem --> Player
PowerSystem --> Enemy

%% ─────────────────────────────
%% SYSTÈMES
%% ─────────────────────────────

class GateSystem {
    <<dataclass>>
    +switch_infos : list~SwitchInfo~
    +gate_infos : list~GateInfo~
    +walls : SpriteList
    +gates : SpriteList
    -_switch_state_map : dict
    +__post_init__() None
    +update() None
    +toggle_switch(switch: Sprite) None
    -_switch_states() dict
    -_set_gate_open(gate: Sprite, is_open: bool) None
}

class CollisionResult {
    <<dataclass>>
    +should_restart : bool
    +score_delta : int
    +teleport_destination : tuple
    +chest_message : str
}

class CollisionSystem {
    <<dataclass>>
    +level : Level
    +player : Player
    +weapon_system : WeaponSystem
    +gate_system : GateSystem
    +crystals_sound : Sound
    +power_system : PowerSystem
    -_teleport_cooldown : int
    -_collected_key_ids : set
    -_opening_chests : set
    +update() CollisionResult
    -_player_touches_enemy() bool
    -_player_falls_in_hole() bool
    -_collect_player_crystals() int
    -_collect_weapon_crystals() int
    -_collect_crystal(crystal: TextureAnimationSprite) None
    -_handle_weapon_enemy_hits() None
    -_remove_enemy_hit(enemy_sprite: TextureAnimationSprite, weapon: Weapon) None
    -_handle_weapon_switch_hits() None
    -_handle_weapon_obstacle_hits() None
    -_handle_key_pickups() None
    -_handle_chest_openings() str
    -_update_opening_chests() None
    -_check_teleportation() tuple
}

class CameraController {
    <<dataclass>>
    +camera : Camera2D
    +player : Player
    +world_width : int
    +world_height : int
    +margin_x : int
    +margin_y : int
    +center_on_player() None
    +update(screen_width: int, screen_height: int) None
    -_clamp_camera_axis(camera_position: float, screen_size: int, world_size: int) float
}

GateSystem --> SwitchInfo
GateSystem --> GateInfo
GateSystem ..> MapParser : evaluate_formula()

CollisionSystem --> CollisionResult
CollisionSystem --> Level
CollisionSystem --> Player
CollisionSystem --> WeaponSystem
CollisionSystem --> GateSystem
CollisionSystem --> PowerSystem
CollisionSystem --> Weapon

CameraController --> Player

%% ─────────────────────────────
%% ASSETS ET CONSTANTES
%% ─────────────────────────────

class Constants {
    <<module>>
    +WINDOW_TITLE
    +SCALE
    +TILE_SIZE
    +PLAYER_MOVEMENT_SPEED
    +SPINNER_MOVEMENT_SPEED
    +BOOMERANG_SPEED
    +BOOMERANG_MAX_DISTANCE
    +BAT_MOVEMENT_SPEED
    +BAT_MOVEMENT_RADIUS
    +SWORD_ATTACK_DURATION
    +SWORD_HITBOX_SIZE
    +SWORD_HITBOX_OFFSET
    +BLOB_PATROL_RADIUS
    +BLOB_MOVEMENT_SPEED
    +BLOB_LINE_OF_SIGHT_MAX
    +BLOB_NAVMESH_SUBDIVISIONS
    +ICE_FRICTION
    +GROUND_FRICTION
    +ICE_MAX_SPEED
    +POWER_DURATION_FRAMES
    +GHOST_ALPHA
}

class Textures {
    <<module>>
    -_load_grid(file, columns, rows, tile_size) list
    -_load_animation_strip(file, frame_count, frame_duration, tile_size) TextureAnimation
    +TEXTURE_GRASS
    +TEXTURE_BUSH
    +TEXTURE_HOLE
    +TEXTURE_SWITCH_OFF
    +TEXTURE_SWITCH_ON
    +TEXTURE_GATE_OPEN
    +TEXTURE_GATE_CLOSED
    +TEXTURE_TELEPORTER
    +TEXTURE_ICE
    +ANIMATION_PLAYER_IDLE_DOWN
    +ANIMATION_PLAYER_IDLE_UP
    +ANIMATION_PLAYER_IDLE_LEFT
    +ANIMATION_PLAYER_IDLE_RIGHT
    +ANIMATION_SWORD_DOWN
    +ANIMATION_SWORD_UP
    +ANIMATION_SWORD_LEFT
    +ANIMATION_SWORD_RIGHT
    +ANIMATION_BOOMERANG
    +ANIMATION_CRYSTAL
    +ANIMATION_SPINNERS
    +ANIMATION_BAT
    +ANIMATION_BLOB
    +ANIMATION_KEY
    +ANIMATION_CHEST
    +ANIMATION_CHEST_OPEN
    +ANIMATION_CHEST_STAYS_OPEN
}

class Sounds {
    <<module>>
    +CRYSTALS_SOUND : Sound
}

GameView --> Constants
GameView --> Sounds
LevelModule --> Textures
Player --> Textures
WeaponSystem --> Textures
SwordWeapon --> Textures
Boomerang --> Textures
GateSystem --> Textures
CollisionSystem --> Textures

%% ─────────────────────────────
%% ORCHESTRATION PRINCIPALE
%% ─────────────────────────────

GameView --> Level
GameView --> Player
GameView --> GateSystem
GameView --> CollisionSystem
GameView --> WeaponSystem
GameView --> PowerSystem
GameView --> CameraController
GameView --> EnemyUpdateContext

LevelModule ..> Map
Map --> LevelModule : données validées
```
