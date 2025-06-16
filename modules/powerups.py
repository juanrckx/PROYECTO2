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
        self.sprites = {PowerupType.EXTRA_LIFE: pygame.image.load("assets/powerups/extra_life.png")}

        self.duration = {PowerupType.BOMB_IMMUNITY: 5000,
                         PowerupType.PHASE_TROUGH: 5000,
                         PowerupType.FREEZE_ENEMIES: 7000,}.get(self.type, 0)

    def apply(self, player):
        if self.type == PowerupType.EXTRA_LIFE:
            player.lives += 1
        elif self.type == PowerupType.EXPLOSION_RANGE

