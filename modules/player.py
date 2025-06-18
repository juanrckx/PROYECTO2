import pygame
from modules.utils import RED, TILE_SIZE, PowerupType
from modules.bomb import Bomb
from modules.weapon import Weapon

class Player:
    def __init__(self, x, y, lives, speed, color, bomb_capacity, character_type):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.hitbox = pygame.Rect(
            x * TILE_SIZE + 5, y * TILE_SIZE + 5,
            TILE_SIZE - 10, TILE_SIZE - 10
        )
        self.lives = lives
        self.speed = speed  # Aumentada la velocidad base
        self.color = color
        #self.item = item
        self.character_type = character_type
        self.base_explosion_range = 2 if character_type == 2 else 1
        self.explosion_range = self.base_explosion_range

        self.bombs = []
        self.bomb_capacity = bomb_capacity
        self.available_bombs = bomb_capacity

        self.key_collected = False

        self.invincible = False
        self.invincible_frames = 0
        self.invincible_duration = 140  # Duración de invencibilidad (frames)
        self.visible = True

        self.stored_powerup = None
        self.active_effects = {
            "bomb_immune": False,
            "phase_through": False,
            "frozen_enemies": False}

        self.weapon = Weapon(self)

    def store_powerup(self, powerup):
        if self.stored_powerup is None:
            self.stored_powerup = powerup
            return True
        return False

    def activate_powerup(self):
        if not self.stored_powerup:
            return
        if self.stored_powerup.type == PowerupType.EXTRA_LIFE:
            self.lives += 1
        elif self.stored_powerup.type == PowerupType.EXTRA_BOMB:
            self.available_bombs += 1
            self.bomb_capacity += 1
        elif self.stored_powerup.type == PowerupType.EXTRA_VELOCITY:
            self.speed = min(self.speed + 1, 10)
        elif self.stored_powerup.type == PowerupType.EXPLOSION_RANGE:
            self.explosion_range += 1
        elif self.stored_powerup.type == PowerupType.BOMB_IMMUNITY:
            self.active_effects["bomb_immune"] = True
            pygame.time.set_timer(pygame.USEREVENT + 10, 5000)  # 5 segundos
        elif self.stored_powerup.type == PowerupType.PHASE_TROUGH:
            self.active_effects["phase_through"] = True
            pygame.time.set_timer(pygame.USEREVENT + 11, 5000)
        elif self.stored_powerup.type == PowerupType.FREEZE_ENEMIES:
            self.active_effects["frozen_enemies"] = True
            pygame.time.set_timer(pygame.USEREVENT + 12, 7000)

        self.stored_powerup = None


    def move(self, dx, dy, game_map, current_level):
        # Movimiento diagonal permitido
        if dx != 0 and dy != 0:
            # Normalizar para mantener velocidad constante en diagonal
            dx = dx * 0.7071
            dy = dy * 0.7071

        # Movimiento en X
        if dx != 0:
            new_hitbox = self.hitbox.move(dx * self.speed, 0)
            if not self.check_collision(new_hitbox, game_map):
                self.hitbox.x = new_hitbox.x
                self.rect.x = self.hitbox.x - 5

        # Movimiento en Y
        if dy != 0:
            new_hitbox = self.hitbox.move(0, dy * self.speed)
            if not self.check_collision(new_hitbox, game_map):
                self.hitbox.y = new_hitbox.y
                self.rect.y = self.hitbox.y - 5

        for powerup in current_level.powerups:
            if self.hitbox.colliderect(powerup.rect):
                if self.store_powerup(powerup):
                    current_level.powerups.remove(powerup)




    def check_collision(self, rect, game_map):
        for block in game_map:
            if not block.destroyed and block.rect.colliderect(rect):
                return True
        return False

    def player_place_bomb(self):
        if self.available_bombs > 0:
            grid_x = self.rect.centerx // TILE_SIZE
            grid_y = self.rect.centery // TILE_SIZE
            self.bombs.append(Bomb(grid_x * TILE_SIZE, grid_y * TILE_SIZE, self))
            self.available_bombs -= 1  # Consumir bomba

    def take_damage(self):
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_frames = self.invincible_duration
            return True
        return False


    def update_invincibility(self):
        if self.invincible:
            self.invincible_frames -= 1

            if self.invincible_frames <= 0:
                self.invincible = False
                self.visible = True

            if self.invincible_frames % 6 == 0:
                self.visible = not self.visible


    def update_weapon(self):
        self.update_invincibility()
        self.weapon.update()

    def shoot(self, direction):
        self.weapon.shoot(direction)


    def get_explosion_pattern(self):
        if self.character_type == 2 or self.explosion_range > self.base_explosion_range:
            return "diamond"
        return "cross"


    def draw(self, surface):
        if not self.invincible or self.visible:
            pygame.draw.rect(surface, self.color, self.rect)
        if self.invincible:
                pygame.draw.rect(surface, RED, self.rect, 2)
        self.weapon.draw(surface)
