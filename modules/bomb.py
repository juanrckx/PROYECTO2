import pygame
from modules.utils import ORANGE, TILE_SIZE, FPS

class Bomb:
    def __init__(self, x, y, player, timer=3, bomb_range=1):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.timer = timer * FPS  # Convertir segundos a frames
        self.range = bomb_range
        self.exploded = False
        self.explosion_timer = 30
        self.explosion_rects = []
        self.player = player

    def update(self):
        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0:
                self.explode(self.player)
        else:
            self.explosion_timer -= 1
        return self.explosion_timer <= 0

    def explode(self, player):
        self.exploded = True
        self.explosion_rects = [self.rect]
        explosion_type = player.get_explosion_pattern()

        # Explosión en forma de cruz con rango limitado
        for i in range(1, self.range + 1):
            directions = [
                    (i, 0),  # Derecha
                    (-i, 0),  # Izquierda
                    (0, i),  # Abajo
                    (0, -i),  # Arriba
                ]

            if explosion_type == "diamond" or self.player.character_type == 2:

                    directions.extend([
            (0, -2),  # Arriba (▲)
            (-1, -1), (0, -1), (1, -1),  # Diagonal superior
            (-2, 0), (-1, 0), (1, 0), (2, 0),  # Horizontal (◄ ♦ ►)
            (-1, 1), (0, 1), (1, 1),  # Diagonal inferior
            (0, 2)  # Abajo (▼)
        ])

            for dx, dy in directions:
                new_rect = pygame.Rect(
                    self.rect.x + dx * TILE_SIZE,
                    self.rect.y + dy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if new_rect not in self.explosion_rects:  # Evita duplicados
                    self.explosion_rects.append(new_rect)

    def draw(self, surface):
        if not self.exploded:
            pygame.draw.rect(surface, (255, 0, 0), self.rect)
        else:
            for rect in self.explosion_rects:
                pygame.draw.rect(surface, ORANGE, rect)
