import pygame
import random
import math

from bomb import Bomb
from utils import TILE_SIZE, WIDTH, HEIGHT


class Boss:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 128, 128)
        self.health = 200
        self.max_health = 200
        self.base_speed = 2.0
        self.current_speed = 0.0
        self.color = (200, 0, 0)

        # Estados y comportamientos
        self.state = "inactive"
        self.phase = 1
        self.attacks = [
            self._random_bombs,
            self._charge_attack,
            self._super_bombs,
            self._invert_controls,
            self._no_bombs_spell
        ]
        self.attack_weights = [0.3, 0.3, 0.2, 0.1, 0.1]  # Probabilidades

        # Temporizadores
        self.initial_cooldown = 180  # 3 segundos
        self.attack_cooldown = 0
        self.stun_timer = 0
        self.charge_timer = 0
        self.ability_duration = 0
        self.boss_bombs = []

        # Ataque de carga
        self.charge_direction = pygame.Vector2(0, 0)
        self.charge_speed_multiplier = 3.0
        self.is_charging = False

        # Efectos especiales
        self.controls_inverted = False
        self.bombs_disabled = False
        self.current_level = None
        self.debug_log = []

    def set_level(self, level):
        self.current_level = level

    def update(self, player, arena_blocks):
        # Cooldown inicial
        if self.initial_cooldown > 0:
            self.initial_cooldown -= 1
            if self.initial_cooldown == 0:
                self.state = "active"
                self._activate_boss()
            return

        # Actualizar efectos temporales
        self._update_effects(player)

        # Comportamiento según estado
        if self.state == "stunned":
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.state = "active"
            return

        if self.state == "charging":
            self._update_charge()
            return

        if self.state == "active":
            self._update_active(player, arena_blocks)

        for bomb in self.boss_bombs[:]:
            if bomb.update(self.current_level):
                # Verificar colisión solo con jugador, no con jefe
                if player.hitbox.colliderect(pygame.Rect(
                        bomb.rect.x - bomb.explosion_range * TILE_SIZE,
                        bomb.rect.y - bomb.explosion_range * TILE_SIZE,
                        bomb.rect.width + bomb.explosion_range * TILE_SIZE * 2,
                        bomb.rect.height + bomb.explosion_range * TILE_SIZE * 2
                )):
                    player.take_damage(1)
                self.boss_bombs.remove(bomb)

    def _activate_boss(self):
        """Efecto dramático al activarse el jefe"""
        # Temblor de pantalla
        # Sonido especial
        self.color = (255, 0, 0)

    def _update_active(self, player, arena_blocks):
        # Cambio de fase
        if self.health <= self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.base_speed *= 1.3
            self.attack_weights = [0.2, 0.4, 0.2, 0.1, 0.1]  # Más carga en fase 2

        # Comportamiento según fase
        if self.phase == 1:
            if random.random() < 0.01 and self.attack_cooldown <= 0:
                self._execute_random_attack(player)
        else:
            self._pursue_player(player)
            if random.random() < 0.03 and self.attack_cooldown <= 0:
                self._execute_random_attack(player)

        self.attack_cooldown = max(0, self.attack_cooldown - 1)

    def _execute_random_attack(self, player):
        attack = random.choices(self.attacks, weights=self.attack_weights, k=1)[0]
        attack(player)
        self.attack_cooldown = random.randint(120, 180)  # 2-3 segundos

    def _super_bombs(self, player):
        if not hasattr(self, 'current_level') or not self.current_level:
            return

        for _ in range(2):  # Solo 2 super bombas
            x = random.randint(TILE_SIZE, WIDTH - TILE_SIZE * 2)
            y = random.randint(TILE_SIZE, HEIGHT - TILE_SIZE * 2)
            bomb = Bomb(x, y, self, True, 5)  # Rango de explosión 5
            bomb.rect.inflate_ip(20, 20)  # Bomba más grande
            self.boss_bombs.append(bomb)

        self.debug_log.append("¡Super bombas lanzadas!")

    def _no_bombs_spell(self, player):
        if player:
            player.can_place_bombs = False
            self.bombs_disabled = True
            self.ability_duration = 300  # 5 segundos
            self.debug_log.append("Bombas desactivadas!")

            # Restablecer después de 5 segundos
            pygame.time.set_timer(pygame.USEREVENT + 20, 5000, True)

    def _invert_controls(self, player):
        if player:
            player.controls_inverted = True
            self.controls_inverted = True
            self.ability_duration = 300  # 5 segundos
            self.debug_log.append("Controles invertidos!")

            # Restablecer después de 5 segundos
            pygame.time.set_timer(pygame.USEREVENT + 30, 5000, True)

    def _pursue_player(self, player):
        # Persecución directa en fase 2
        if not player:
            return

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1, int(math.sqrt(dx * dx + dy * dy)))

        self.rect.x += (dx / dist) * self.current_speed
        self.rect.y += (dy / dist) * self.current_speed

        # Mantener dentro de la arena
        self.rect.x = max(TILE_SIZE, min(WIDTH - TILE_SIZE - self.rect.width, self.rect.x))
        self.rect.y = max(TILE_SIZE, min(HEIGHT - TILE_SIZE - self.rect.height, self.rect.y))

    def _random_bombs(self, player):
        # Lanzar 5 bombas en posiciones aleatorias
        for _ in range(5):
            x = random.randint(TILE_SIZE, WIDTH - TILE_SIZE * 2)
            y = random.randint(TILE_SIZE, HEIGHT - TILE_SIZE * 2)
            if hasattr(self, 'current_level') and self.current_level:
                self.boss_bombs.append(Bomb(x, y, self, False, 3))
        self.attack_cooldown = 120  # 2 segundos de cooldown



    def _charge_attack(self, player):
        if not player or self.is_charging:
            return

        self.state = "charging"
        self.charge_direction = pygame.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        ).normalize()

        self.charge_timer = 60  # 1 segundo de carga
        self.is_charging = True
        self.base_speed *= self.charge_speed_multiplier
        self.color = (255, 100, 100)  # Color de carga

    def _update_charge(self):
        if self.charge_timer <= 0:
            self._end_charge()
            return

        self.charge_timer -= 1

        # Movimiento durante la carga
        self.rect.x += self.charge_direction.x * self.base_speed
        self.rect.y += self.charge_direction.y * self.base_speed

        # Verificar colisión con paredes
        if self._check_wall_collision():
            self._on_charge_collision()

    def _check_wall_collision(self):
        # Verificar bordes
        if (self.rect.left <= TILE_SIZE or self.rect.right >= WIDTH - TILE_SIZE or
                self.rect.top <= TILE_SIZE or self.rect.bottom >= HEIGHT - TILE_SIZE):
            return True

        # Verificar bloques
        if not self.current_level:
            return False

        for block in self.current_level.map:
            if not block.destroyed and self.rect.colliderect(block.rect):
                return True
        return False

    def _on_charge_collision(self):
        self.state = "stunned"
        self.stun_timer = 90  # 1.5 segundos
        self.is_charging = False
        self.base_speed /= self.charge_speed_multiplier
        self.color = (255, 200, 0)  # Color de aturdimiento
        self.attack_cooldown = 180  # 3 segundos de cooldown

    def _update_effects(self, player):
        if self.ability_duration > 0:
            self.ability_duration -= 1
            if self.ability_duration <= 0:
                self._reset_effects(player)

        # Actualizar velocidad suavemente
        self.current_speed += (self.base_speed - self.current_speed) * 0.1

    def _reset_effects(self, player):
        if player:
            player.controls_inverted = False
            player.can_place_bombs = True
        self.controls_inverted = False
        self.bombs_disabled = False


    def _end_charge(self):
        self.state = "active"
        self.is_charging = False
        self.base_speed /= self.charge_speed_multiplier
        self.color = (200, 0, 0)  # Color normal
        self.attack_cooldown = 120  # 2 segundos de cooldown

    def take_damage(self, amount):
        if self.state == "stunned":  # Doble daño cuando está aturdido
            amount *= 2

        self.health = max(0, self.health - amount)

        # Cambio de fase
        if self.health <= self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.base_speed *= 1.3

        return self.health <= 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

        # Barra de vida
        health_width = int(self.rect.width * (self.health / self.max_health))
        health_bar = pygame.Rect(self.rect.x, self.rect.y - 15, health_width, 10)
        pygame.draw.rect(surface, (0, 255, 0), health_bar)

        # Indicadores de estado
        if self.controls_inverted:
            pygame.draw.polygon(surface, (255, 0, 255), [
                (self.rect.right - 10, self.rect.top + 10),
                (self.rect.right - 20, self.rect.top + 20),
                (self.rect.right - 10, self.rect.top + 20)
            ])

        if self.bombs_disabled:
            pygame.draw.line(surface, (255, 0, 0),
                             (self.rect.right - 25, self.rect.top + 10),
                             (self.rect.right - 15, self.rect.top + 20), 3)
        for bomb in self.boss_bombs:
            bomb.draw(surface)