import pygame
from utils import  TILE_SIZE, FPS

class Bomb:
    def __init__(self, x, y, player, is_super, explosion_range, timer=3):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.timer = timer * FPS  # Convertir segundos a frames
        self.explosion_range = explosion_range
        self.exploded = False
        self.explosion_timer = 30
        self.explosion_rects = []
        self.player = player
        self.is_super = is_super



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

        # Definir patrones de explosión
        base_pattern = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if hasattr(player, 'get_explosion_pattern') and player.get_explosion_pattern() == "diamond":
            base_pattern.extend([(1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (0, 2), (-2, 0), (0, -2)])

        for dx, dy in base_pattern:
            for i in range(1, self.explosion_range + 1):
                new_rect = pygame.Rect(
                    self.rect.x + dx * i * TILE_SIZE,
                    self.rect.y + dy * i * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )

                # Solo verificar colisión si NO tenemos indestructible_bomb
                if hasattr(player, 'item_effects') and player.item_effects.get("indestructible_bomb"):
                    if any(not block.destructible and block.rect.colliderect(new_rect)
                           for block in current_level.map):
                        break

                self.explosion_rects.append(new_rect)









    def draw(self, surface):
        if not self.exploded:
            if self.is_super:
                pygame.draw.circle(surface, (255, 255, 0), self.rect.center, self.rect.width // 2 + 5, 2)
            else:
                pygame.draw.rect(surface, (255, 0, 0), self.rect)
