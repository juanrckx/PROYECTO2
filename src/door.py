import pygame
from utils import GREEN, RED, TILE_SIZE, WHITE, DEFAULT_FONT


class Door:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.open = False

    def draw(self, surface):
        color = GREEN if self.open else RED
        pygame.draw.rect(surface, color, self.rect)
        text = DEFAULT_FONT.render("→", True, WHITE)
        surface.blit(text, (self.rect.x + 10, self.rect.y + 5))


class Key:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.collected = False
        self.revealed = False
        self.texture_collected = pygame.image.load("assets/textures/materials/key.png").convert_alpha()
        self.texture_collected = pygame.transform.scale(self.texture_collected, (TILE_SIZE, TILE_SIZE))
        self.texture = pygame.image.load("assets/textures/materials/brick_material.png").convert_alpha()
        self.texture = pygame.transform.scale(self.texture, (TILE_SIZE, TILE_SIZE))

    def draw(self, surface):
        if not self.collected and not self.revealed:
            surface.blit(self.texture, self.rect)
        if not self.collected and self.revealed:
            surface.blit(self.texture_collected, self.rect)
