import random

import pygame
from modules.utils import TILE_SIZE, PowerupType, WIDTH, HEIGHT
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
        self.animations = self.load_character_animations(character_type)
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.idle_animation_speed = 0.1  # Más lento para idle
        self.last_update = pygame.time.get_ticks()
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
        self.item_effects = {"speed_+5": False,
                            "bullet_trace": False,
                            "shotgun": False,
                            "bullet_heal": False,
                            "1life_shield": False,
                            "double_damage": False,
                            "revive": False,
                            "superbomb": False}
        self.has_shield = False
        self.revive_chance = 0
        self.bullet_hits = 0
        self.enemy_damage_multiplier = 0
        self.bomb_pierce_indestructible = False
        self.game = game  # Guarda referencia
        self.was_phasing = None
        self.facing = "down"
        self.load_character_animations(character_type)

    def load_character_animations(self, character_type):
        """Carga animaciones con verificación de errores robusta"""
        animations = {
            "idle": {"down": [], "up": [], "left": [], "right": []},
            "walk": {"down": [], "up": [], "left": [], "right": []}}


        try:
            character_sprites = {
                0: "bomber.png",
                1: "tanky.png",
                2: "pyro.png",
                3: "cleric.png"
            }

            if character_type not in character_sprites:
                raise ValueError(f"Tipo de personaje {character_type} no válido")

            sheet_path = f"assets/textures/characters/{character_sprites[character_type]}"

            # 2. Cargar la imagen
            sheet = pygame.image.load(sheet_path).convert_alpha()
            print(f"Spritesheet cargada: {sheet_path} ({sheet.get_width()}x{sheet.get_height()})")

            # 3. Calcular dimensiones de cada frame
            cols = 3  # 3 columnas (frames de animación)
            rows = 4  # 3 filas (direcciones)
            frame_width = sheet.get_width() // cols
            frame_height = sheet.get_height() // rows

            direction_rows = {
                0: "down",
                1: "left",
                2: "right",
                3: "up"
            }

            # 4. Asignar frames a las animaciones
            for row in range(rows):
                direction = direction_rows[row]
                for col in range(cols):
                    # Extraer frame
                    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (col * frame_width, row * frame_height, frame_width, frame_height))
                    scaled_frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))

                    # Para walk: usar los 3 frames
                    animations["walk"][direction].append(scaled_frame)

                    # Para idle: usar el frame central (col=1)
                    if col == 1:
                        animations["idle"][direction].append(scaled_frame)

                        # Opcional: crear 2-3 frames de idle con variaciones sutiles
                        for i in range(2):
                            modified_frame = scaled_frame.copy()
                            # Pequeña modificación para frame alternativo
                            if i == 0:
                                pygame.draw.rect(modified_frame, (0, 0, 0, 10), (0, 0, TILE_SIZE, 1))  # Sombra superior
                            animations["idle"][direction].append(modified_frame)

        except Exception as e:
            print(f"Error cargando animaciones: {e}")
            # Crear fallback
            fallback_frame = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(fallback_frame, self.color, (0, 0, TILE_SIZE, TILE_SIZE))
            for anim in animations:
                for direction in animations[anim]:
                    animations[anim][direction] = [fallback_frame]

        return animations


    def update_animation(self):
        """Actualiza la animación actual"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now

            current_anim = self.animations[self.current_animation][self.facing]

            # Lógica diferente para walk vs idle
            if self.current_animation == "walk":
                # Ciclo completo de 3 frames (0-1-2-0...)
                self.animation_frame = (self.animation_frame + 1) % 3
            else:
                # Para idle: ciclo más lento entre los frames disponibles
                self.animation_frame = (self.animation_frame + 0.15) % len(current_anim)

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

    def apply_item_effect(self, effect_name):
        # Resetear efectos previos si es necesario
        self.reset_item_effects()

        if effect_name == "speed_boost":
            self.speed += 5
            self.item_effects["speed_boost"] = True

        elif effect_name == "homing_bullets":
            self.item_effects["homing_bullets"] = True

        elif effect_name == "shotgun":
            self.item_effects["shotgun"] = True

        elif effect_name == "bullet_heal":
            self.item_effects["bullet_heal"] = True
            self.bullet_hits = 0

        elif effect_name == "one_shield":
            self.has_shield = True
            self.item_effects["one_shield"] = True

        elif effect_name == "double_damage":
            self.damage += 5
            self.enemy_damage_multiplier = 2
            self.item_effects["double_damage"] = True

        elif effect_name == "revive_chance":
            self.revive_chance = 0.25
            self.item_effects["revive_chance"] = True

        elif effect_name == "indestructible_bomb":
            self.bomb_pierce_indestructible = True
            self.item_effects["indestructible_bomb"] = True

    def reset_item_effects(self):
                # Restablecer todos los efectos de items
        if "speed_boost" in self.item_effects:
            self.speed /= 1.5
        if "double_damage" in self.item_effects:
            self.damage -= 5
            self.enemy_damage_multiplier = 1

        self.item_effects = {}
        self.has_shield = False
        self.revive_chance = 0
        self.bomb_pierce_indestructible = False




    def move(self, dx, dy, game_map, current_level):

        if dx < 0:
            self.facing = "left"
        elif dx > 0:
            self.facing = "right"
        elif dy < 0:
            self.facing = "up"
        elif dy > 0:
            self.facing = "down"

        is_moving = dx != 0 or dy != 0
        new_animation = "walk" if is_moving else "idle"

        if self.active_effects.get("phase_through", False):
            # Movimiento sin colisiones (excepto bordes del mapa)
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            self.hitbox.x = self.rect.x + 5
            self.hitbox.y = self.rect.y + 5
        else:
            # Movimiento diagonal permitido
            if is_moving:
                dx = dx * 0.7071
                dy = dy * 0.7071
                if self.current_animation != new_animation:
                    self.current_animation = new_animation
                    self.animation_frame = 0  # Reiniciar al primer frame de walk
                # Normalizar para mantener velocidad constante en diagonal

            else:
                if self.current_animation != "idle":
                    self.current_animation = "idle"
                    self.animation_frame = 0  # Reiniciar animación idle

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
        self.update_animation()




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
        if self.has_shield:
            self.has_shield = False
            self.invincible = True
            self.invincible_frames = self.invincible_duration
            return False

        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_frames = self.invincible_duration

            if self.lives <= 0 and random.random() < self.revive_chance:
                self.lives = 1
                return False

            return True
        return False


    def update_invincibility(self):
        if self.invincible:
            self.invincible_frames -= 1

            if self.invincible_frames % 6 == 0:
                self.visible = not self.visible

            if self.invincible_frames <= 0:
                self.invincible = False
                self.visible = True




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
        if not self.visible:
            return

        try:
            # Para walk: frame_index entero (0-1-2)
            if self.current_animation == "walk":
                frame_index = int(self.animation_frame) % 3
            # Para idle: frame_index puede ser float para transiciones suaves
            else:
                frame_index = int(self.animation_frame) % len(self.animations["idle"][self.facing])

            current_frame = self.animations[self.current_animation][self.facing][frame_index]
            surface.blit(current_frame, self.rect)



        except Exception as e:
            print(f"Error dibujando: {e}")
            pygame.draw.rect(surface, self.color, self.rect)

        self.weapon.draw(surface)
