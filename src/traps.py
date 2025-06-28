import pygame
from utils import TILE_SIZE

class TrapType:
    FIRE = 0
    ICE = 1
    POISON = 2


class Trap:
    def __init__(self, x, y, trap_type):
        self.x = x
        self.y = y
        self.type = trap_type
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.cooldown = 0  # Frames de espera entre activaciones

    def draw(self, surface):
        colors = {
            TrapType.FIRE: (255, 0, 0),
            TrapType.ICE: (0, 255, 255),
            TrapType.POISON: (100, 255, 100),
        }
        pygame.draw.rect(surface, colors[self.type], self.rect)

    def activate(self, player):
        if self.cooldown > 0:
            self.cooldown -= 1
            return

        if self.type == TrapType.FIRE:
            player.take_damage(1)

        elif self.type == TrapType.ICE:
            if not hasattr(player, "ice_applied") or not player.ice_applied:
                player.original_speed = player.speed
                player.speed = max(1, player.speed - 1)
                player.ice_applied = True
                pygame.time.set_timer(pygame.USEREVENT + 50, 3000)

        elif self.type == TrapType.POISON:
            player.take_damage(1)  # <-- Cambiar aquí

    # Si tienes más tipos de trampas, se manejan igual aquí...

        self.cooldown = 60



class TrapManager:
    def __init__(self, traps_list):
        self.traps = [Trap(x, y, tipo) for x, y, tipo in traps_list]

    def draw(self, surface):
        for trap in self.traps:
            trap.draw(surface)

    def check_collision(self, player):
        for trap in self.traps:
            if player.hitbox.colliderect(trap.rect):
                trap.activate(player)

