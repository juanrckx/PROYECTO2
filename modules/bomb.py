import pygame
from modules.utils import  TILE_SIZE, FPS

class Bomb:
    def __init__(self, x, y, player, timer=3, bomb_range=1):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.timer = timer * FPS  # Convertir segundos a frames
        self.range = bomb_range
        self.exploded = False
        self.explosion_timer = 30
        self.explosion_rects = []
        self.player = player


    def update(self, current_level = None):
        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0 and current_level is not None:
                self.explode(self.player, current_level)
                return True
        else:
            self.explosion_timer -= 1
        return self.explosion_timer <= 0


    def explode(self, player, current_level):
        self.exploded = True
        self.explosion_rects = [self.rect]
        explosion_type = player.get_explosion_pattern()

        # Explosión en forma de cruz con rango limitado
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:  # Direcciones base
            for i in range(1, self.range + 1):
                new_rect = pygame.Rect(
                    self.rect.x + dx * i * TILE_SIZE,
                    self.rect.y + dy * i * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )

                # Verifica colisión con bloques indestructibles
                block_collision = any(
                    not block.destructible and block.rect.colliderect(new_rect)
                    for block in current_level.map
                )
                if block_collision:
                    break  # Detiene la explosión en esta dirección

                if new_rect not in self.explosion_rects:
                    self.explosion_rects.append(new_rect)

            # Añade explosión en diamante si es necesario (para Pyro o powerup)
            if explosion_type == "diamond" or self.player.character_type == 2:
                for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:  # Diagonales
                    diamond_rect = pygame.Rect(
                        self.rect.x + dx * i * TILE_SIZE,
                        self.rect.y + dy * i * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    if diamond_rect not in self.explosion_rects:
                        self.explosion_rects.append(diamond_rect)


    def draw(self, surface):
        if not self.exploded:
            pygame.draw.rect(surface, (255, 0, 0), self.rect)
