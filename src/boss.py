
import pygame
import random
from src.modules.utils import TILE_SIZE, WIDTH, HEIGHT
from src.modules.bomb import Bomb

class Boss:
    def __init__(self, x, y):
        self.rect: pygame.Rect = pygame.Rect(x, y, 128, 128)
        self.health = 200
        self.max_health = 200
        self.speed = 1.5
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

    def update(self, player, current_time, arena_blocks):
        # Actualizar timers
        if self.is_exhausted:
            if pygame.time.get_ticks() - self.exhaustion_timer >= 10000:
                self.is_exhausted = False
                self.speed = 0.5

        if self.controls_inverted:
            if pygame.time.get_ticks() - self.controls_inverted_timer >= 10000:
                player.controls_inverted = False
                self.controls_inverted = False

        self.update_bombs(player, current_level=arena_blocks)

        if self.health > self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.speed = 2
            self.color = (255, 165, 0)

        currentTime = pygame.time.get_ticks()
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

        if not self.is_exhausted:
            self.move_towards_player(player)


    def _random_bombs(self, player, _):
        for _ in range(5):
            bomb_x = random.randint(1, WIDTH // TILE_SIZE - 1) * TILE_SIZE
            bomb_y = random.randint(1, HEIGHT // TILE_SIZE - 1) * TILE_SIZE
            self.boss_bombs.append(Bomb(bomb_x * TILE_SIZE, bomb_y * TILE_SIZE, self, False, 2))

    def _invert_controls(self, player, _):
        player.controls_inverted = True
        self.controls_inverted = True
        self.controls_inverted_timer = pygame.time.get_ticks()

    def _no_bombs_spell(self, player, _):
        if self.health < self.max_health // 2:
            player.can_place_bombs = False
            pygame.time.set_timer(pygame.USEREVENT + 20, 10000, True)

            if hasattr(player, 'game'):
                player.game.show_message("¡Bloqueo de bombas! 5 segundos", 10000)  # 10 segundos


    def _super_bombs(self, _, __):
        for _ in range(2):
            x = random.randint(1, WIDTH // TILE_SIZE - 1) * TILE_SIZE
            y = random.randint(1, WIDTH // TILE_SIZE - 1) * TILE_SIZE
            bomb = Bomb(x, y, self, True, 5)
            bomb.rect.inflate_ip(20, 20)
            self.boss_bombs.append(bomb)

    def _charge_attack(self, player, _):
        direction = pygame.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)

        if direction.length() > 0:
            direction = direction.normalize()

        self.rect.x += direction.x * self.speed * 5
        self.rect.y += direction.y * self.speed * 5

        self.is_exhausted = True
        self.exhaustion_timer = pygame.time.get_ticks()

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
        self.rect.clamp_ip(pygame.Rect(TILE_SIZE, TILE_SIZE, WIDTH - 2 * TILE_SIZE, HEIGHT - 2 * TILE_SIZE))

    def update_bombs(self, player, current_level):
        for bomb in self.boss_bombs[:]:
            if bomb.update(current_level):
                current_level.check_bomb_collisions(bomb, player)
                self.boss_bombs.remove(bomb)


    def draw(self, surface):
        # Dibujar al jefe (placeholder)
        pygame.draw.rect(surface, (200, 0, 0), self.rect)

        # Barra de vida
        health_ratio = self.health / self.max_health
        health_width = int(self.rect.width * health_ratio)
        health_bar = pygame.Rect(self.rect.x, self.rect.y - 10, health_width, 5)
        pygame.draw.rect(surface, (0, 255, 0), health_bar)

        # Dibujar bombas
        for bomb in self.boss_bombs:
            bomb.draw(surface)