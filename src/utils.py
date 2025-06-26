import os

import pygame
from enum import Enum


def load_fonts(size=20):
    try:
        # Asegúrate de que pygame.font esté inicializado
        if not pygame.font.get_init():
            pygame.font.init()

        font_path = os.path.join("..", "assets", "fonts", "default.ttf")
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            print(f"Advertencia: No se encontró {font_path}. Usando fuente del sistema.")
    except Exception as e:
        print(f"Error crítico al cargar fuente: {e}")

    # Fallback a fuentes seguras
    try:
        return pygame.font.SysFont("Arial", size)
    except:
        return pygame.font.Font(None, size)  # Fuente por defecto de Pygame


# No cargues las fuentes aquí. Solo declara las variables.
DEFAULT_FONT = None
TITLE_FONT = None

DEFAULT_FONT = load_fonts(20)
TITLE_FONT = load_fonts(30)

MAP_WIDTH, MAP_HEIGHT = 1280, 800
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60
GREEN, RED, WHITE, YELLOW, BROWN, GRAY, BLUE, ORANGE, BLACK = ((0, 255, 0), (255, 0, 0), (255, 255, 255), (255, 215, 0),
                                                               (150, 75, 0),
                                                               (100, 100, 100), (0, 0, 255), (255, 100, 0), (0, 0, 0))


class GameState(Enum):
    MENU = 0
    CHARACTER_SELECT = 1
    GAME = 2
    INTERLEVEL = 3
    GAME_OVER = 4
    VICTORY = 5


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    FINAL_BOSS = 3


class PowerupType(Enum):
    EXTRA_LIFE = 0
    EXTRA_BOMB = 1
    EXTRA_VELOCITY = 2
    EXTRA_DAMAGE = 3
    EXPLOSION_RANGE = 4
    BOMB_IMMUNITY = 5
    PHASE_TROUGH = 6
    FREEZE_ENEMIES = 7


class ScrollingBackground:
    def __init__(self, image_path, speed=1):
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.width = self.image.get_width()
        self.scroll = 0
        self.speed = speed

    def update(self):
        self.scroll -= self.speed
        if self.scroll < -self.width:
            self.scroll = 0

    def draw(self, surface):
        surface.blit(self.image, (self.scroll, 0))
        surface.blit(self.image, (self.scroll + self.width, 0))

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.smoothness = 0.15

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):

        x = -target.rect.centerx + self.width // 2
        y = -target.rect.centery + self.width // 2

        x = min(0, max(-(MAP_WIDTH - self.width), x))
        y = min(0, max(-(MAP_HEIGHT - self.height), y))

        self.camera.x += (x - self.camera.x) * self.smoothness
        self.camera.y += (y - self.camera.y) * self.smoothness