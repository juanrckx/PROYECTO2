import math

import pygame

from boss import Boss
from utils import RED, WIDTH, HEIGHT, Difficulty


class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.bullets = []
        self.cooldown = 0
        self.base_damage = 1
        self.damage = self.base_damage
        self.speed=5
        self.max_bullets = 10

    def apply_damage_boost(self, amount):
        self.damage += self.base_damage + amount

    def shoot(self, direction):
        if self.cooldown <= 0 and len(self.bullets) < self.max_bullets:
            x, y = self.owner.rect.centerx, self.owner.rect.centery

            if self.owner.item_effects["shotgun"]:
                self._shotgun_shot(direction, x, y)
            else:
                dx, dy = 0, 0
                if direction == "up":
                    dy = -1
                elif direction == "down":
                    dy = 1
                elif direction == "left":
                    dx = -1
                elif direction == "right":
                    dx = 1

                self._normal_shot(dx, dy, x, y)

            self.cooldown = 20



    def _normal_shot(self, dx, dy, x, y):
        bullet = Bullet(
            x, y,
            dx, dy,
            self.speed,
            self.damage,
            self.owner
        )
        if self.owner.item_effects["homing_bullets"]:
            bullet.homing = True
        self.bullets.append(bullet)

    def _shotgun_shot(self, direction, x, y):
        pellet_count = 5
        spread_angle = 45
        base_damage = self.damage * 0.6

        if direction == "up":
            base_angle = 90
            spread_axis = "horizontal"

        elif direction == "down":
            base_angle = 270
            spread_axis = "horizontal"

        elif direction == "left":
            base_angle = 180
            spread_axis = "vertical"
        else:
            base_angle = 0
            spread_axis = "vertical"

        for i in range(pellet_count):
            if spread_axis == "horizontal":
                angle_offset = (i - (pellet_count - 1) / 2) * (spread_angle / (pellet_count - 1))
                current_angle = math.radians(base_angle + angle_offset)
            else:
                angle_offset = (i - (pellet_count - 1) / 2) * (spread_angle / (pellet_count - 1))
                current_angle = math.radians(base_angle + angle_offset)

            dx = math.cos(current_angle)
            dy = -math.sin(current_angle)

            bullet = Bullet(x, y, dx, dy, self.speed * 0.8, base_damage, self.owner)
            if self.owner.item_effects["homing_bullets"]:
                bullet.homing = True
                bullet.homing_strength = 0.1
            self.bullets.append(bullet)




    def update(self, current_level):
        self.cooldown = max(0, self.cooldown - 1)
        for bullet in self.bullets[:]:
            if bullet.update(current_level):
                self.bullets.remove(bullet)

    def draw(self, surface):
        for bullet in self.bullets:
            bullet.draw(surface)





class Bullet:
    def __init__(self, x, y, dx, dy, speed, damage, owner):
        self.rect = pygame.Rect(x- 4, y- 4, 8, 8)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.homing = False
        self.homing_target = None
        self.homing_strength = 0.2
        self.owner = owner

    def update(self, current_level):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

        # Lógica de homing (si está activo)
        if self.homing and not self.homing_target:
            self._acquire_target(current_level.enemies)

        if self.homing and self.homing_target:
            self._home_to_target()

        for enemy in current_level.enemies[:]:
            if enemy != "dead" and self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)


                if self.owner.item_effects["bullet_heal"]:
                    self.owner.bullet_heal_counter += 1
                    if self.owner.bullet_heal_counter >= 20:
                        self.owner.lives = min(self.owner.lives + 1, 5)
                        self.owner.bullet_heal_counter = 0
                return True

        for block in current_level.map:
            if not block.destroyed and self.rect.colliderect(block.rect):
                return True

        # Retorna True si la bala sale de la pantalla
        return (self.rect.x < 0 or self.rect.x > WIDTH or
                self.rect.y < 0 or self.rect.y > HEIGHT)

    def _acquire_target(self, enemies):
        """Asigna el enemigo más cercano como objetivo"""
        if not enemies:
            return

        # Filtra enemigos vivos
        alive_enemies = [e for e in enemies if e.state != "dead"]

        if alive_enemies:
            # Encuentra el enemigo más cercano
            self.homing_target = min(
                alive_enemies,
                key=lambda e: ((e.rect.centerx - self.rect.centerx) ** 2 +
                               (e.rect.centery - self.rect.centery) ** 2) ** 0.5)


    def _home_to_target(self):
        """Ajusta la dirección hacia el objetivo"""
        if not self.homing_target or self.homing_target.state == "dead":
            self.homing_target = None
            return

        # Calcula vector hacia el objetivo
        target_x, target_y = self.homing_target.rect.center
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)  # Evita división por cero

        # Normaliza y mezcla con la dirección actual
        self.dx = self.dx * (1 - self.homing_strength) + (dx / distance) * self.homing_strength
        self.dy = self.dy * (1 - self.homing_strength) + (dy / distance) * self.homing_strength

        # Normaliza la dirección final
        norm = (self.dx ** 2 + self.dy ** 2) ** 0.5
        if norm > 0:
            self.dx /= norm
            self.dy /= norm

    def draw(self, surface):

        if self.homing:
            # Dibuja un aura pulsante
            alpha = 100 + int(100 * math.sin(pygame.time.get_ticks() * 0.01))
            aura = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(aura, (255, 50, 50, alpha), (6, 6), 6)
            surface.blit(aura, (self.rect.x - 2, self.rect.y - 2))

        pygame.draw.circle(surface, (255, 200, 0), self.rect.center, 3)