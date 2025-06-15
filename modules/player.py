import pygame
from modules.utils import RED, TILE_SIZE
from modules.bomb import Bomb

class Player:
    def __init__(self, x, y, lives, speed, color, bomb_capacity):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.hitbox = pygame.Rect(
            x * TILE_SIZE + 5, y * TILE_SIZE + 5,
            TILE_SIZE - 10, TILE_SIZE - 10
        )
        self.lives = lives
        self.speed = speed  # Aumentada la velocidad base
        self.color = color

        self.bombs = []
        self.bomb_capacity = bomb_capacity
        self.available_bombs = bomb_capacity  # Bombas disponibles

        self.key_collected = False

        self.invincible = False
        self.invincible_frames = 0
        self.invincible_duration = 140  # Duración de invincibilidad (frames)
        self.visible = True


    def move(self, dx, dy, game_map):
        # Movimiento diagonal permitido
        if dx != 0 and dy != 0:
            # Normalizar para mantener velocidad constante en diagonal
            dx = dx * 0.7071
            dy = dy * 0.7071

        # Movimiento en X
        if dx != 0:
            new_hitbox = self.hitbox.move(dx * self.speed, 0)
            if not self.check_collision(new_hitbox, game_map):
                self.hitbox.x = new_hitbox.x
                self.rect.x = self.hitbox.x - 5

        # Movimiento en Y
        if dy != 0:
            new_hitbox = self.hitbox.move(0, dy * self.speed)
            if not self.check_collision(new_hitbox, game_map):
                self.hitbox.y = new_hitbox.y
                self.rect.y = self.hitbox.y - 5

    def check_collision(self, rect, game_map):
        for block in game_map:
            if not block.destroyed and block.rect.colliderect(rect):
                return True
        return False

    def place_bomb(self):
        if self.available_bombs > 0:
            grid_x = self.rect.centerx // TILE_SIZE
            grid_y = self.rect.centery // TILE_SIZE
            self.bombs.append(Bomb(grid_x * TILE_SIZE, grid_y * TILE_SIZE))
            self.available_bombs -= 1  # Consumir bomba

    def take_damage(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_frames = self.invincible_duration
            return True
        return False


    def update_invincibility(self):
        if self.invincible:
            self.invincible_frames -= 1

            if self.invincible_frames <= 0:
                self.invincible = False
                self.visible = True

            if self.invincible_frames % 6 == 0:
                self.visible = not self.visible


    def draw(self, surface):
        if not self.invincible or self.visible:
            pygame.draw.rect(surface, self.color, self.rect)
        if self.invincible:
                pygame.draw.rect(surface, RED, self.rect, 2)
