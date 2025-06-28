import pygame
from utils import  GRAY, TILE_SIZE

class Block:
    def __init__(self, x, y, destructible=False):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.destructible = destructible
        self.has_key = False
        self.destroyed = False

        if not destructible:
            self.texture = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.texture.fill(GRAY)

        else:
            self.texture = pygame.image.load("assets/textures/materials/brick_material.png").convert_alpha()
            self.texture = pygame.transform.scale(self.texture, (TILE_SIZE, TILE_SIZE))

    def draw(self, surface):
        if not self.destroyed:
            surface.blit(self.texture, self.rect)

class Trap:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.type = type  # "fuego", "veneno", "hielo"
        self.texture = pygame.image.load(f"assets/textures/traps/{type}.png").convert_alpha()
        self.texture = pygame.transform.scale(self.texture, (TILE_SIZE, TILE_SIZE))

    def draw(self, surface):
        surface.blit(self.texture, self.rect)


