from enum import Enum

WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60
GREEN, RED, WHITE, YELLOW, BROWN, GRAY, BLUE, ORANGE, BLACK = ((0, 255, 0), (255, 0, 0), (255, 255, 255), (255, 215, 0), (150, 75, 0),
                                                        (100, 100, 100), (0, 0, 255), (255, 100, 0), (0, 0, 0))


class GameState(Enum):
    MENU = 0
    CHARACTER_SELECT = 1
    GAME = 2
    GAME_OVER = 3
    VICTORY = 4


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    FINAL_BOSS = 4

class PowerupType(Enum):
    EXTRA_LIFE = 0
    EXTRA_BOMB = 1
    EXTRA_VELOCITY = 2
    EXTRA_DAMAGE = 3
    EXPLOSION_RANGE = 4
    BOMB_IMMUNITY = 5
    PHASE_TROUGH = 6
    FREEZE_ENEMIES = 7
