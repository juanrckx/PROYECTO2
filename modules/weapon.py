import pygame
from modules.utils import RED, WIDTH, HEIGHT

class Weapon:
    def __init__(self, owner):
        self.owner = owner
        self.bullets = []
        self.cooldown = 0
        self.base_damage = 1
        self.damage = self.base_damage
        self.speed=10
        self.max_bullets = 10

    def apply_damage_boost(self, amount):
        self.damage += self.base_damage + amount

    def shoot(self, direction):
        if self.cooldown <= 0 and len(self.bullets) < self.max_bullets:
            x = self.owner.rect.centerx
            y = self.owner.rect.centery
            self.bullets.append(Bullet(x, y, direction, self.speed, self.damage))
            self.cooldown = 15


    def update(self, current_level):
        self.cooldown = max(0, self.cooldown - 1)
        for bullet in self.bullets[:]:
            if bullet.update(current_level):
               self.bullets.remove(bullet)

    def draw(self, surface):
        for bullet in self.bullets:
            bullet.draw(surface)





class Bullet:
    def __init__(self, x, y, direction, speed, damage):
        self.rect = pygame.Rect(x- 4, y- 4, 8, 8)
        self.direction = direction
        self.speed = speed
        self.damage = damage

    def update(self, current_level):
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed

        for block in current_level.map:
            if not block.destroyed and self.rect.colliderect(block.rect):
                return True

        # Retorna True si la bala sale de la pantalla
        return (self.rect.x < 0 or self.rect.x > WIDTH or
                self.rect.y < 0 or self.rect.y > HEIGHT)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)