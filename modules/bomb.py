import pygame
from modules.utils import ORANGE, TILE_SIZE, FPS

class Bomb:
    def __init__(self, x, y, timer=3, bomb_range=1):  # Reducido el rango de explosión
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.timer = timer * FPS  # Convertir segundos a frames
        self.range = bomb_range
        self.exploded = False
        self.explosion_timer = 30
        self.explosion_rects = []

    def update(self):
        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0:
                self.explode()
        else:
            self.explosion_timer -= 1
        return self.explosion_timer <= 0

    def explode(self):
        self.exploded = True
        self.explosion_rects = [self.rect]

        # Explosión en forma de cruz con rango limitado
        for i in range(1, self.range + 1):
            # Derecha
            self.explosion_rects.append(pygame.Rect(
                self.rect.x + i * TILE_SIZE,
                self.rect.y,
                TILE_SIZE, TILE_SIZE
            ))
            # Izquierda
            self.explosion_rects.append(pygame.Rect(
                self.rect.x - i * TILE_SIZE,
                self.rect.y,
                TILE_SIZE, TILE_SIZE
            ))
            # Arriba
            self.explosion_rects.append(pygame.Rect(
                self.rect.x,
                self.rect.y - i * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            ))
            # Abajo
            self.explosion_rects.append(pygame.Rect(
                self.rect.x,
                self.rect.y + i * TILE_SIZE,
                TILE_SIZE, TILE_SIZE
            ))


    def draw(self, surface):
        if not self.exploded:
            pygame.draw.rect(surface, (255, 0, 0), self.rect)
        else:
            for rect in self.explosion_rects:
                pygame.draw.rect(surface, ORANGE, rect)
