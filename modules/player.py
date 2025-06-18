import pygame
from modules.utils import RED, TILE_SIZE, PowerupType, WIDTH, HEIGHT
from modules.bomb import Bomb
from modules.weapon import Weapon

class Player:
    def __init__(self, x, y, lives, speed, color, bomb_capacity, character_type, game, damage=0.5):
        self.rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.hitbox = pygame.Rect(
            x * TILE_SIZE + 5, y * TILE_SIZE + 5,
            TILE_SIZE - 10, TILE_SIZE - 10
        )
        self.lives = lives
        self.speed = speed  # Aumentada la velocidad base
        self.color = color
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
        self.damage = damage
        #self.item = item
        self.game = game  # Guarda referencia
        self.was_phasing = None

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
            if self.available_bombs == self.bomb_capacity:
                self.bomb_capacity += 1

        elif self.stored_powerup.type == PowerupType.EXTRA_VELOCITY:
            self.speed = min(self.speed + 1, 10)

        elif self.stored_powerup.type == PowerupType.EXTRA_DAMAGE:
            self.weapon.apply_damage_boost(1)

        elif self.stored_powerup.type == PowerupType.EXPLOSION_RANGE:
            self.explosion_range += 1

        elif self.stored_powerup.type == PowerupType.BOMB_IMMUNITY:
            self.active_effects["bomb_immune"] = True

        elif self.stored_powerup.type == PowerupType.PHASE_TROUGH:
            self.active_effects["phase_through"] = True
            self.was_phasing = True
            pygame.time.set_timer(pygame.USEREVENT + 11, 5000, loops=1)

        elif self.stored_powerup.type == PowerupType.FREEZE_ENEMIES:
            self.game.frozen_enemies = True
            pygame.time.set_timer(pygame.USEREVENT + 12, 7000, loops=1)
            print("Enemigos congelados")

        self.stored_powerup = None

    def apply_item_effect(self, effect):
        if effect == "speed_+5":
            self.speed += 5

        elif effect == "bullet_trace":
            self.bullet_trace = True

        elif effect == "shotgun":
            self.shotgun = True

        elif effect == "bullet_heal":
            self.bullet_heal = True

        elif effect == "1life_shield":
            self.shield = True

        elif effect == "double_damage":
            self.damage += 5
            self.damage_multiplier = 2.0
        elif effect == "revive":
            self.revive_capacity = True


    def move(self, dx, dy, game_map, current_level):

        if self.active_effects.get("phase_through", False):
            # Movimiento sin colisiones (excepto bordes del mapa)
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            self.hitbox.x = self.rect.x + 5
            self.hitbox.y = self.rect.y + 5
        else:
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

        self.rect.x = max(0, min(WIDTH - TILE_SIZE, self.rect.x))
        self.rect.y = max(0, min(HEIGHT - TILE_SIZE, self.rect.y))




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


    def update_weapon(self, current_level):
        self.update_invincibility()
        self.weapon.update(current_level)

    def shoot(self, direction):
        self.weapon.shoot(direction)


    def get_explosion_pattern(self):
        if self.character_type == 2 or self.explosion_range > self.base_explosion_range:
            return "diamond"
        return "cross"

    def update_phase_effect(self, current_level):
        if not self.active_effects.get("phase_through", False)and self.was_phasing:
            self.was_phasing = False
            new_x, new_y = self.find_valid_position(current_level)
            self.rect.x = new_x
            self.rect.y = new_y
            self.hitbox.x = self.rect.x + 5
            self.hitbox.y = self.rect.y + 5


    def find_valid_position(self, current_level):
        directions = [
            (0, 0),  # Posición actual
            (0, -1),  # Arriba
            (0, 1),  # Abajo
            (-1, 0),  # Izquierda
            (1, 0)  # Derecha
        ]

        for dx, dy in directions:
            new_x = self.rect.x + dx * TILE_SIZE
            new_y = self.rect.y + dy * TILE_SIZE
            temp_rect = pygame.Rect(new_x, new_y, TILE_SIZE, TILE_SIZE)

            # Verifica si la nueva posición es válida
            if not any(block.rect.colliderect(temp_rect) for block in current_level.map if not block.destroyed):
                return new_x, new_y

        return self.rect.x, self.rect.y  # Si no encuentra, mantiene posición (poco probable)

    def draw(self, surface):
        if not self.invincible or self.visible:
            pygame.draw.rect(surface, self.color, self.rect)
        if self.invincible:
                pygame.draw.rect(surface, RED, self.rect, 2)
        self.weapon.draw(surface)
