import pygame
from modules.utils import GREEN, RED, BROWN, YELLOW, TILE_SIZE


class Door:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.open = False

    def draw(self, surface):
        color = GREEN if self.open else RED
        pygame.draw.rect(surface, color, self.rect)


class Key:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.collected = False

    def draw(self, surface):
        if not self.collected:
            pygame.draw.rect(surface, BROWN, self.rect)
        else:
            pygame.draw.rect(surface, YELLOW, self.rect)
