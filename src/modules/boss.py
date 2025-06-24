from time import sleep

import pygame
import random
from typing import List
from modules.utils import TILE_SIZE, WIDTH, HEIGHT
from modules.bomb import Bomb

class Boss:
    def __init__(self, x, y):
        self.rect: pygame.Rect = pygame.Rect(x, y, 128, 128)
        self.health = 200
        self.max_health = 200
        self.speed = 3
        self.color = (200, 0, 0)
        self.attacks = [self._random_bombs, self._invert_controls, self._no_bombs_spell,
                        self._super_bombs, self._charge_attack]
        self.current_attack = None
        self.attack_cooldown = 0
        self.boss_bombs = []
        self.is_exhausted = False
        self.exhaustion_timer = 0
        self.controls_inverted = False
        self.controls_inverted_timer = 0
        self.phase = 1
        self.state = "moving"

    def update(self, player, current_time, arena_blocks):
        # Actualizar timers
        if self.is_exhausted:
            self.exhaustion_timer -= 1
            if self.exhaustion_timer <= 0:
                self.is_exhausted = False

        if not self.is_exhausted:
            self.move_towards_player(player)

        if self.controls_inverted:
            self.controls_inverted_timer -= 1
            if self.controls_inverted_timer <= 0:
                player.controls_inverted = False
                self.controls_inverted = False

        self.update_bombs(player, current_level=)

        # Cambiar fase si la vida baja del 50%
        if self.health < self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.speed += 1  # Aumentar dificultad

        # Lógica de ataques
        if self.attack_cooldown <= 0 and not self.is_exhausted:
            self.current_attack = random.choice(self.attacks)
            if self.phase == 2 and random.random() < 0.3:  # 30% de chance de combinar ataques
                secondary_attack = random.choice(self.attacks)
                secondary_attack(player, arena_blocks)
            self.current_attack(player, arena_blocks)
            self.attack_cooldown = random.randint(180, 300)  # 3-5 segundos (60 FPS)
        else:
            self.attack_cooldown -= 1

        # Movimiento básico (perseguir al jugador)
        if not self.is_exhausted:
            dx = 1 if player.rect.centerx > self.rect.centerx else -1
            dy = 1 if player.rect.centery > self.rect.centery else -1
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def _random_bombs(self, player, arena_blocks):
        for _ in range(5):
            bomb_x = random.randint(0, WIDTH // TILE_SIZE) * TILE_SIZE
            bomb_y = random.randint(0, HEIGHT // TILE_SIZE) * TILE_SIZE
            self.boss_bombs.append(Bomb(bomb_x * TILE_SIZE, bomb_y * TILE_SIZE, self, False, 2))

    def _invert_controls(self, player, _):
        player.controls_inverted = True
        self.controls_inverted = True
        self.controls_inverted_timer = 600

    def _no_bombs_spell(self, player, _):
        if self.health < self.max_health // 2:
            player.can_place_bombs = False


    def _super_bombs(self, _, arena_blocks):
        for _ in range(2):
            x = random.randint(0, WIDTH // TILE_SIZE) * TILE_SIZE
            y = random.randint(0, WIDTH // TILE_SIZE) * TILE_SIZE
            bomb = Bomb(x, y, _, explosion_range = 5, is_super=True)
            bomb.rect.inflate_ip(20, 20)
            self.boss_bombs.append(bomb)

    def _charge_attack(self, player, _):
        # Calcular dirección
        direction_x = player.rect.centerx - self.rect.centerx
        direction_y = player.rect.centery - self.rect.centery

        # Evitar división por cero
        if direction_x == 0 and direction_y == 0:
            # Si están en la misma posición, elegir dirección aleatoria
            direction_x = random.choice([-1, 1])
            direction_y = random.choice([-1, 1])

        charge_direction = pygame.Vector2(direction_x, direction_y).normalize() * 10

        # Aplicar movimiento
        self.rect.x += charge_direction.x
        self.rect.y += charge_direction.y

        # Estado de agotamiento
        self.is_exhausted = True
        self.exhaustion_timer = 300  # 5 segundos (60 FPS * 5)

    def boss_take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.state = "dead"

    def move_towards_player(self, player):
        direction = pygame.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction = direction.normalize()

        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed

    def execute_attack(self, player, arena_blocks, current_time):
        attack = random.choice(self.attacks)
        attack(player,arena_blocks)
        self.attack_cooldown = random.randint(180, 300)

    def update_bombs(self, player, current_level):
        for bomb in self.boss_bombs[:]:
            if bomb.update(current_level):
                current_level.check_bomb_collisions(bomb, player)
                self.boss_bombs.remove(bomb)


    def draw(self, surface):
        # Dibujar al jefe (placeholder)
        pygame.draw.rect(surface, (200, 0, 0), self.rect)

        # Barra de vida
        health_width = int(self.rect.width * (self.health / self.max_health))
        health_bar = pygame.Rect(self.rect.x, self.rect.y - 10, health_width, 5)
        pygame.draw.rect(surface, (0, 255, 0), health_bar)