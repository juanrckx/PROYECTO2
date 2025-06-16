from datetime import datetime, timedelta

import pygame
import random
from modules.utils import PowerupType

class Powerup:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = random.choice(list(PowerupType))
        self.spawn_time = datetime.now()
        self.lifespan = timedelta(seconds=90)
        self.active = True
        self.sprites = {PowerupType.EXTRA_LIFE: pygame.image.load("assets/textures/powerups/life_up2.png"),
                        PowerupType.EXTRA_BOMB: pygame.image.load("assets/textures/powerups/bomb_up.png"),
                        PowerupType.EXTRA_VELOCITY: pygame.image.load("assets/textures/powerups/speedup.png"),
                        PowerupType.EXPLOSION_RANGE: pygame.image.load("assets/textures/powerups/dmg_up.png"),
                        PowerupType.BOMB_IMMUNITY: pygame.image.load("assets/textures/powerups/bomb_inmunity.png"),
                        PowerupType.PHASE_TROUGH: pygame.image.load("assets/textures/powerups/phase_through.png"),
                        PowerupType.FREEZE_ENEMIES: pygame.image.load("assets/textures/powerups/freeze_enemies.png")}


    def update(self):
        if datetime.now() - self.spawn_time > self.lifespan:
            self.active = False

    def draw(self, surface):
        if self.active:
            surface.blit(self.sprites[self.type], self.rect)

