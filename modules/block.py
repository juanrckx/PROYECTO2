import pygame
from modules.utils import YELLOW, GRAY, TILE_SIZE

class Block:
    def __init__(self, x, y, destructible=False, has_key=False):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.destructible = destructible
        self.has_key = has_key
        self.destroyed = False
        self.revealed_key = False

        if not destructible:
            self.texture = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.texture.fill(GRAY)

        else:
            self.texture = pygame.image.load("assets/textures/materials/brick_material.png").convert_alpha()
            self.texture = pygame.transform.scale(self.texture, (TILE_SIZE, TILE_SIZE))

    def draw(self, surface):
        if not self.destroyed:
            surface.blit(self.texture, self.rect)

            if self.has_key and not self.revealed_key:
                pygame.draw.circle(surface, YELLOW, self.rect.center, TILE_SIZE // 3)

