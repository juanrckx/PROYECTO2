import pygame
import random
from typing import List
from modules.level import Level
from modules.utils import TILE_SIZE
from modules.bomb import Bomb

class Boss:
    def __init__(self, x, y):
        self.rect: pygame.Rect = pygame.Rect(x, y, 128, 128)
        self.health = 200
        self.speed = 3
        self.attacks = [self._random_bombs, self._invert_controls, self._no_bombs_spell,
                        self._super_bombs, self._charge_attack]
        self.current_attack = None
        self.attack_cooldown = 0
        self.boss_bombs = []

    def update(self, player, arena_blocks: List[pygame.Rect]):
        if self.attack_cooldown <= 0:
            self.current_attack = random.choice(self.attacks)
            self.attack_cooldown = 300
        else:
            self.attack_cooldown -= 1

        if self.current_attack:
            self.current_attack(player, arena_blocks)

    def place_bomb(self):
            grid_x = self.rect.centerx // TILE_SIZE
            grid_y = self.rect.centery // TILE_SIZE
            self.boss_bombs.append(Bomb(grid_x * TILE_SIZE, grid_y * TILE_SIZE))


    def _random_bombs(self, player, arena_blocks):
        for _ in range(5):
            x, y = Level.find_valid_position()
            bomb_pos = (random.randint(x, y), random.randint(x, y))


    def _invert_controls(self, player):
        player.controls_inverted = True
        pygame.time.set_timer(pygame.USEREVENT, 5000)

    def _no_bombs_spell(self, player):
        player.can_place_bombs = False
        pygame.time.set_timer(pygame.USEREVENT, 5000)

    #def _super_bombs(self, player, arena_blocks):

    #def _charge_attack(self, player, arena_blocks):
