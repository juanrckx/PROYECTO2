from datetime import datetime, timedelta

import pygame
import random
from utils import PowerupType

class Powerup:
    _sprites = None

    @classmethod
    def load_sprites(cls):
        if cls._sprites is None:
            cls._sprites = {PowerupType.EXTRA_LIFE: pygame.image.load("assets/textures/powerups/life_up2.png").convert_alpha(),
                        PowerupType.EXTRA_BOMB: pygame.image.load("assets/textures/powerups/bomb_up.png").convert_alpha(),
                        PowerupType.EXTRA_VELOCITY: pygame.image.load("assets/textures/powerups/speedup.png").convert_alpha(),
                        PowerupType.EXTRA_DAMAGE: pygame.image.load("assets/textures/powerups/dmg_up.png").convert_alpha(),
                        PowerupType.EXPLOSION_RANGE: pygame.image.load("assets/textures/powerups/explosion_range.png").convert_alpha(),
                        PowerupType.BOMB_IMMUNITY: pygame.image.load("assets/textures/powerups/bomb_inmunity.png").convert_alpha(),
                        PowerupType.PHASE_TROUGH: pygame.image.load("assets/textures/powerups/phase_through.png").convert_alpha(),
                        PowerupType.FREEZE_ENEMIES: pygame.image.load("assets/textures/powerups/freeze_enemies.png").convert_alpha()}

        for key in cls._sprites:
            cls._sprites[key] = pygame.transform.scale(cls._sprites[key], (42, 42))

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 42, 42)
        self.type = random.choice(list(PowerupType))
        self.spawn_time = datetime.now()
        self.lifespan = timedelta(seconds=90)
        self.active = True
        powerup_types = list(PowerupType)
        weights = [
            0.3,  # EXTRA_LIFE
            0.7,  # EXTRA_BOMB
            0.2,  # EXTRA_VELOCITY
            0.2,  # EXTRA_DAMAGE
            0.09,  # EXPLOSION_RANGE
            0.10,  # BOMB_IMMUNITY
            0.05,  # PHASE_TROUGH
            0.05  # FREEZE_ENEMIES
        ]
        self.type = random.choices(powerup_types, weights=weights, k=1)[0]

    def update(self):
        if datetime.now() > self.spawn_time + self.lifespan:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        surface.blit(self._sprites[self.type], self.rect)

