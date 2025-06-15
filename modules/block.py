import pygame
from modules.utils import BROWN, YELLOW, GRAY, TILE_SIZE

class Block:
    def __init__(self, x, y, destructible=False, has_key=False):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.destructible = destructible
        self.has_key = has_key
        self.destroyed = False
        self.revealed_key = False

    def draw(self, surface):
        if not self.destroyed:
            if self.has_key and self.revealed_key:
                color = YELLOW
            elif self.destructible:
                color = BROWN
            else:
                color = GRAY
            pygame.draw.rect(surface, color, self.rect)
