import pygame
from utils import GREEN, RED, TILE_SIZE, WHITE, DEFAULT_FONT, WIDTH


class Door:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.open = False
        self.wood_color =

    def draw(self, surface):
        if self.open:
            # Dividir la puerta en dos partes que se "abren"
            if self.rect.x == 0 or self.rect.x >= WIDTH - TILE_SIZE:  # Puertas laterales
                pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y, TILE_SIZE // 2, TILE_SIZE))
                pygame.draw.rect(surface, GREEN, (self.rect.x + TILE_SIZE // 2, self.rect.y, TILE_SIZE // 2, TILE_SIZE))
                # Línea central
                pygame.draw.line(surface, WHITE,
                                 (self.rect.x + TILE_SIZE // 2, self.rect.y),
                                 (self.rect.x + TILE_SIZE // 2, self.rect.y + TILE_SIZE), 3)
            else:  # Puertas superior/inferior
                pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE // 2))
                pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y + TILE_SIZE // 2, TILE_SIZE, TILE_SIZE // 2))
                pygame.draw.line(surface, WHITE,
                                 (self.rect.x, self.rect.y + TILE_SIZE // 2),
                                 (self.rect.x + TILE_SIZE, self.rect.y + TILE_SIZE // 2), 3)
        else:
            pygame.draw.rect(surface, RED, self.rect)


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
