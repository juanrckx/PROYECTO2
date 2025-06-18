import pygame
from modules.utils import TILE_SIZE
import random

class Enemy:
    def __init__(self, x, y, enemy_type):
        self.type = enemy_type
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.set_attributes()
        self.direction = pygame.Vector2(0, 0)
        self.change_direction_timer = 0
        self.state = "moving"  # moving, tired, dead


    def set_attributes(self):
        if self.type == 1:  # Normal
            self.speed = 2  # Aumentada velocidad
            self.health = 1
            self.color = (255, 0 ,0)
        elif self.type == 2:  # Fast
            self.speed = 4  # Aumentada velocidad
            self.health = 1
            self.color = (255, 165, 0)
        elif self.type == 3:  # Tank
            self.speed = 1.5  # Reducida velocidad
            self.health = 2
            self.color = (139, 69, 19)

    def update(self, game_map):
        if self.state == "dead":
            return

        self.change_direction_timer += 1

        if self.change_direction_timer > 60 or random.random() < 0.02:
            self.direction = pygame.Vector2(
                random.choice([-1, 0, 1]),
                random.choice([-1, 0, 1]))

            if self.direction.length() > 0:
                self.direction.normalize_ip()

            self.change_direction_timer = 0

        new_rect = self.rect.copy()
        new_rect.x += self.direction.x * self.speed
        new_rect.y += self.direction.y * self.speed

        # Verificar colisión con bloques
        can_move = True
        for block in game_map:
            if not block.destroyed and block.rect.colliderect(new_rect):
                can_move = False
                break

        # Si puede moverse, actualizar posición
        if can_move:
            self.rect = new_rect
        else:
            # Si no puede moverse, cambiar dirección inmediatamente
            self.change_direction_timer = 60  # Forzar cambio de dirección

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.state = "dead"


    def draw(self, surface):
        if self.state != "dead":
            pygame.draw.rect(surface, self.color, self.rect)
