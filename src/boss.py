
import pygame
import random
from utils import TILE_SIZE, WIDTH, HEIGHT
from bomb import Bomb


DEBUG_MODE = True  # Cambiar a False para desactivar los debugs
BOSS_DEBUG_LOG = "boss_debug.log"

def boss_debug(message, condition=True):
    if DEBUG_MODE and condition:
        print(f"[BOSS DEBUG] {message}")
        with open(BOSS_DEBUG_LOG, "a") as f:
            f.write(f"{message}\n")



class Boss:
    def __init__(self, x, y):
        self.rect: pygame.Rect = pygame.Rect(x, y, 128, 128)
        self.health = 200
        self.max_health = 200
        self.base_speed = 3.0
        self.target_speed = 3.0
        self.current_speed = 0.0
        self.speed_transition = 0.15
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
        self.last_attack_time = 0
        self.attack_delay = 5000
        self.current_level = None
        self.last_path_update = 0
        self.last_direction = (0, 0)
        self.exhausted_speed = 0.5
        self.charge_multiplier = 5
        self.recovery_duration = 1000
        self.phase_transition_complete = False


    def set_level(self, level):
        self.current_level = level

    def update(self, player, arena_blocks):
        current_time = pygame.time.get_ticks()

        if self.state == "inactive":
            return

        self._update_exhaustion()
        self._update_speed()
        self._handle_attacks(player, arena_blocks)

        if self.phase == 1:
            # Ataques cada 5 segundos
            if current_time - self.last_attack_time > 7500:
                self.last_attack_time = current_time
                attack = random.choice([self._random_bombs, self._super_bombs, self._invert_controls])
                attack(player, arena_blocks)
        else:
            self._phase_two_behavior(player,arena_blocks)

        if (self.controls_inverted and
                current_time - self.controls_inverted_timer > 10000):
            player.controls_inverted = False
            self.controls_inverted = False


            # Actualización de bombas
        self.update_bombs(player, self.current_level)


    def _check_wall_collision(self, rect):
        """Verifica colisión con bordes y bloques indestructibles"""
        # Verificar bordes de pantalla
        if (rect.left < TILE_SIZE or rect.right > WIDTH - TILE_SIZE or
                rect.top < TILE_SIZE or rect.bottom > HEIGHT - TILE_SIZE):
            return True

        # Verificar bloques indestructibles
        if not hasattr(self, 'current_level') or not self.current_level:
            return False

        margin = 10  # Margen de tolerancia
        test_rect = rect.inflate(-margin, -margin)

        return any(
            not block.destructible and
            not block.destroyed and
            test_rect.colliderect(block.rect)
            for block in self.current_level.map
        )

    def _phase_two_behavior(self, player, arena_blocks):
        """Comportamiento después del 50% de vida"""
        # Destruir todos los bloques destructibles al entrar en fase 2
        if not self.phase_transition_complete:
            self._destroy_all_destructible_blocks()
            self.phase_transition_complete = True
            self.base_speed *= 1.5  # Aumentar velocidad

        # Comportamiento agresivo
        self.smart_move_towards(player)

        # Ataques más frecuentes
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > 3000:  # Cada 3 segundos
            self.last_attack_time = current_time
            self.current_attack = random.choice(self.attacks)
            self.current_attack(player, arena_blocks)

    def _destroy_destructible_blocks(self):
        """Destruye bloques destructibles al azar"""
        if not hasattr(self, 'current_level'):
            return

        for block in self.current_level.map[:]:
            if block.destructible and random.random() < 0.3:  # 30% de probabilidad por bloque
                block.destroyed = True
                self.current_level.map.remove(block)

    def _destroy_all_destructible_blocks(self):
        """Destruye todos los bloques destructibles"""
        if not hasattr(self, 'current_level'):
            return

        self.current_level.map = [b for b in self.current_level.map if not b.destructible]

    def _update_exhaustion(self):
        """Maneja el estado de agotamiento con transición suave"""
        if self.is_exhausted:
            recovery_progress = min(1.0, (pygame.time.get_ticks() - self.exhaustion_timer - 4000) / 1000)

            if recovery_progress >= 1.0:
                self.is_exhausted = False
                boss_debug("Recuperación completa")
            elif recovery_progress >= 0:
                # Recuperación gradual durante el último segundo
                speed_range = self.base_speed - self.exhausted_speed
                self.target_speed = self.exhausted_speed + speed_range * recovery_progress
        else:
            self.target_speed = self.base_speed

    def _handle_attacks(self, player, arena_blocks):
        """Maneja la lógica de ataques"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_delay and not self.is_exhausted:
            if self.phase == 2 and random.random() < 0.3 and self.health < self.max_health * 0.25:
                self.current_attack = random.sample(self.attacks, 2)
                for attack in self.current_attack:
                    attack(player, arena_blocks)
            else:
                self.current_attack = random.choice(self.attacks)
                self.current_attack(player, arena_blocks)

            self.last_attack_time = current_time
            self.attack_delay = random.randint(3000, 5000)

    def _update_speed(self):
        """Suaviza los cambios de velocidad"""
        self.current_speed += (self.target_speed - self.current_speed) * self.speed_transition
        self.current_speed = max(0.1, min(self.base_speed * 1.5, self.current_speed))


    def _random_bombs(self, _, __):
        boss_debug("ATAQUE: Bombas aleatorias (5 bombas)")
        for _ in range(5):
            bomb_x = random.randint(1, WIDTH // TILE_SIZE - 1) * TILE_SIZE
            bomb_y = random.randint(1, HEIGHT // TILE_SIZE - 1) * TILE_SIZE
            self.boss_bombs.append(Bomb(bomb_x * TILE_SIZE, bomb_y * TILE_SIZE, self, False, 2))

    def _invert_controls(self, player, _):
        boss_debug("ATAQUE: Inversión de controles (10 segundos)")
        pygame.time.set_timer(pygame.USEREVENT + 30, 10000, True)  # USEREVENT + 30 para controles
        player.controls_inverted = True

        self.controls_inverted = True
        self.controls_inverted_timer = pygame.time.get_ticks()
        pygame.time.set_timer(pygame.USEREVENT + 30, 10000, 1)

    def _no_bombs_spell(self, player, _):
        if self.health < self.max_health // 2:
            boss_debug("ATAQUE: Bloqueo de bombas (5 segundos)")
            player.can_place_bombs = False
            pygame.time.set_timer(pygame.USEREVENT + 20, 10000, True)



    def _super_bombs(self, _, __):
        boss_debug("ATAQUE: Super bombas (2 bombas de gran alcance)")
        if self.health < self.max_health // 2:
            for _ in range(2):
                x = random.randint(1, WIDTH // TILE_SIZE - 1) * TILE_SIZE
                y = random.randint(1, WIDTH // TILE_SIZE - 1) * TILE_SIZE
                bomb = Bomb(x, y, self, True, 5)
                bomb.rect.inflate_ip(20, 20)
                self.boss_bombs.append(bomb)

    def _charge_attack(self, player, _):
        """Ataque de carga con transición suave"""
        if self.health < self.max_health // 2:
            # Pre-carga: aceleración gradual
            for i in range(1, 6):
                self.target_speed = self.base_speed * (self.charge_multiplier * (i / 5))
                self._update_speed()
                pygame.time.delay(30)

            # Movimiento de carga
            direction = pygame.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            if direction.length() > 0:
                direction = direction.normalize()

            for _ in range(10):
                self.rect.x += direction.x * self.current_speed / 2
                self.rect.y += direction.y * self.current_speed / 2
                pygame.time.delay(15)

            # Postcarga: agotamiento
            self.is_exhausted = True
            self.exhaustion_timer = pygame.time.get_ticks()
            self.target_speed = self.exhausted_speed

    def move_towards_player(self, player):
        """Movimiento directo hacia el jugador"""
        direction = pygame.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )

        if direction.length() > 0:
            direction = direction.normalize()
            self.last_direction = (direction.x, direction.y)

            self.rect.x += direction.x * self.current_speed
            self.rect.y += direction.y * self.current_speed

        # Mantener dentro de límites
        self.rect.clamp_ip(pygame.Rect(
            TILE_SIZE, TILE_SIZE,
            WIDTH - 2 * TILE_SIZE,
            HEIGHT - 2 * TILE_SIZE
        ))

    def check_collision(self, rect):
        if not hasattr(self, 'current_level') or not self.current_level:
            return False

        # Considerar el tamaño del jefe
        margin = 10  # Margen de tolerancia
        test_rect = rect.inflate(-margin, -margin)

        return any(
            not block.destructible and
            test_rect.colliderect(block.rect)
            for block in self.current_level.map
            if not block.destroyed
        )

    def get_safe_directions(self, target_x, target_y):
        """Versión más robusta que siempre encuentra alguna dirección"""
        directions = []
        test_distance = TILE_SIZE + 5  # Margen adicional

        # Calculamos vector hacia el objetivo
        dx_target = 1 if target_x > self.rect.centerx else -1
        dy_target = 1 if target_y > self.rect.centery else -1

        # Orden de prioridad de direcciones (8 direcciones)
        direction_priority = [
            (dx_target, dy_target),  # Diagonal hacia objetivo (máxima prioridad)
            (dx_target, 0),  # Horizontal hacia objetivo
            (0, dy_target),  # Vertical hacia objetivo
            (1, 0), (-1, 0), (0, 1), (0, -1),  # Cardinales
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonales
        ]

        # Verificar colisiones
        for dx, dy in direction_priority:
            test_rect = self.rect.copy()
            test_rect.x += dx * test_distance
            test_rect.y += dy * test_distance

            if not self.check_collision(test_rect):
                directions.append((dx, dy))

        # Fallback: Si no hay direcciones, intentar movimientos mínimos
        if not directions:
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                test_rect = self.rect.copy()
                test_rect.x += dx * (test_distance // 2)  # Medio tile
                test_rect.y += dy * (test_distance // 2)

                if not self.check_collision(test_rect):
                    directions.append((dx, dy))
                    break

        return directions or [(0, 0)]  # Asegurar que siempre retorne algo


    def smart_move_towards(self, player):
        """Movimiento inteligente que evita obstáculos"""
        if not hasattr(self, 'current_level') or not self.current_level:
            return self.move_towards_player(player)  # Fallback básico

        # 1. Obtener dirección ideal hacia el jugador
        dx = 1 if player.rect.centerx > self.rect.centerx else -1
        dy = 1 if player.rect.centery > self.rect.centery else -1

        # 2. Obtener direcciones seguras disponibles
        safe_directions = self.get_safe_directions(player.rect.centerx, player.rect.centery)

        # 3. Elegir la mejor dirección disponible
        if safe_directions:
            # Priorizar dirección hacia el jugador
            if (dx, 0) in safe_directions:
                best_dir = (dx, 0)
            elif (0, dy) in safe_directions:
                best_dir = (0, dy)
            else:
                best_dir = random.choice(safe_directions)
        else:
            # Si no hay direcciones seguras, quedarse quieto
            best_dir = (0, 0)

        # 4. Aplicar movimiento
        self.rect.x += best_dir[0] * self.base_speed
        self.rect.y += best_dir[1] * self.base_speed

    def boss_take_damage(self, amount):
        previous_health = self.health
        self.health -= amount



        if self.health < self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.current_speed += 1
            boss_debug("¡CAMBIO DE FASE! (1->2)")
        elif self.health <= 0:
            self.state = "dead"

            boss_debug("¡JEFE DERROTADO!")


    def update_bombs(self, player, current_level):
        # Validación de parámetros
        if self.current_level is None:
            return

        for bomb in self.boss_bombs[:]:
            if bomb.update(current_level):
                current_level.check_bomb_collisions(bomb, player)
                self.boss_bombs.remove(bomb)

    def debug_draw(self, surface, camera=None):
        """Dibuja información de debug para el jefe"""
        if camera:
            render_pos = self.rect.move(camera.camera.topleft)
        else:
            render_pos = self.rect

        # Dibujar área de colisión
        pygame.draw.rect(surface, (255, 0, 0, 128), render_pos, 1)

        # Dibujar radio de visión/ataque
        pygame.draw.circle(surface, (255, 165, 0, 50), render_pos.center, 200, 1)

        # Dibujar estado actual
        state_text = f"Estado: {self.state}"
        font = pygame.font.SysFont(None, 20)
        text_surface = font.render(state_text, True, (255, 255, 255))
        surface.blit(text_surface, (render_pos.x, render_pos.y - 20))

    def draw(self, surface):
        """Dibuja al jefe con indicadores de estado"""
        pygame.draw.rect(surface, self.color, self.rect)

        # Barra de vida
        health_ratio = self.health / self.max_health
        health_width = int(self.rect.width * health_ratio)
        health_bar = pygame.Rect(self.rect.x, self.rect.y - 10, health_width, 5)
        pygame.draw.rect(surface, (0, 255, 0), health_bar)

        # Indicador de estado
        state_color = (255, 165, 0) if self.is_exhausted else (200, 0, 0)
        pygame.draw.circle(surface, state_color, (self.rect.right - 10, self.rect.top + 10), 5)

        # Dibujar bombas
        for bomb in self.boss_bombs:
            bomb.draw(surface)