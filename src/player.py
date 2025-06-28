import random

import pygame
from utils import TILE_SIZE, PowerupType, WIDTH, HEIGHT, Difficulty, MAP_WIDTH, MAP_HEIGHT, WHITE, DEFAULT_FONT
from bomb import Bomb
from weapon import Weapon

class Player:
    def __init__(self, x, y, lives, speed, color, bomb_capacity, character_type, game):
        current_level = game.levels[game.current_level_index]
        spawn_x, spawn_y = current_level.player_spawn if hasattr(current_level, 'player_spawn') else (x, y)
        self.rect = pygame.Rect(spawn_x * TILE_SIZE, spawn_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.hitbox = pygame.Rect(
            spawn_x * TILE_SIZE + 5, spawn_y * TILE_SIZE + 5,
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
        self.can_place_bombs = True

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
        self.damage = 1
        self.item_effects = {"speed_boost": False,
                            "homing_bullets": False,
                            "shotgun": False,
                            "bullet_heal": False,
                            "has_shield": False,
                            "double_damage": False,
                            "revive_chance": False,
                            "indestructible_bomb": True}
        self.permanent_items = []
        self.item_surfaces = self._load_item_surfaces()
        self.bullet_heal_counter = 0
        self.base_speed = speed
        self.revive_chance = 0
        self.enemy_damage_multiplier = 1.0
        self.game = game  # Guarda referencia
        self.was_phasing = None
        self.facing = "down"
        self.load_character_animations(character_type)

    def _load_item_surfaces(self):
        """Carga las superficies de los items"""

        items = {"speed_boost": "the_fool.png",
                            "homing_bullets": "the_magician.png",
                            "shotgun": "the_high_priestess.png",
                            "bullet_heal": "the_lovers.png",
                            "has_shield": "the_chariot.png",
                            "double_damage": "the_devil.png",
                            "revive_chance": "the_sun.png",
                            "indestructible_bomb": "the_tower.png"}
        surfaces = {}
        for effect, img in items.items():
            try:
                path = f"assets/textures/items/{img}"
                surf = pygame.image.load(path).convert_alpha()
                surfaces[effect] = pygame.transform.scale(surf, (32, 32))
            except:
                surfaces[effect] = self._create_fallback_icon(effect)
        return surfaces

    def _create_fallback_icon(self, effect):
        """Crea un ícono simple para efectos sin imagen"""
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (100, 100, 255), (0, 0, 32, 32), border_radius=4)
        text = DEFAULT_FONT.render(effect[:3], True, WHITE)
        surf.blit(text, (16 - text.get_width() // 2, 16 - text.get_height() // 2))
        return surf


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

        self.stored_powerup = None

    def apply_item_effect(self, effect_name):
        if effect_name not in [item['effect'] for item in self.permanent_items]:
            self.permanent_items.append({
                "effect": effect_name,
                "surface": self.item_surfaces.get(effect_name)
            })
        # Resetear efectos previos si es necesario
        self.reset_item_effects()

        if effect_name == "speed_boost":
            self.speed = self.base_speed + 5
            self.item_effects["speed_boost"] = True

        elif effect_name == "homing_bullets":
            self.item_effects["homing_bullets"] = True

        elif effect_name == "shotgun":
            self.item_effects["shotgun"] = True

        elif effect_name == "bullet_heal":
            self.item_effects["bullet_heal"] = True
            self.bullet_heal_counter = 0

        elif effect_name == "has_shield":
            self.item_effects["has_shield"] = True

        elif effect_name == "double_damage":
            self.damage += 5
            self.enemy_damage_multiplier = 2.0
            self.item_effects["double_damage"] = True

        elif effect_name == "revive_chance":
            self.item_effects["revive_chance"] = 0.25

        elif effect_name == "indestructible_bomb":
            self.item_effects["indestructible_bomb"] = True

    def reset_item_effects(self):
                # Restablecer todos los efectos de items
        if self.item_effects["speed_boost"]:
            self.speed = self.base_speed


        self.item_effects = {k: False for k in self.item_effects}
        self.item_effects["revive_chance"] = False



    def move(self, dx, dy, game_map, current_level):
        if hasattr(self, 'controls_inverted') and self.controls_inverted:
            dx, dy = -dx, -dy
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

            # Límites del mapa según el nivel
            if current_level.difficulty == Difficulty.FINAL_BOSS:
                # Para el nivel del boss usamos el mapa extendido
                self.rect.x = max(0, min(MAP_WIDTH - self.rect.width, self.rect.x))
                self.rect.y = max(0, min(MAP_HEIGHT - self.rect.height, self.rect.y))
            else:
                # Para niveles normales usamos las dimensiones estándar
                self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))
                self.rect.y = max(0, min(HEIGHT - self.rect.height, self.rect.y))

            # Actualizar hitbox después de movimiento
            self.hitbox.x = self.rect.x + 5
            self.hitbox.y = self.rect.y + 5

            if current_level.difficulty == Difficulty.TRANSITION_ROOM:
                # Verificar recolección de llave física
                if (current_level.key and not current_level.key.collected and
                        self.hitbox.colliderect(current_level.key.rect)):
                    current_level.key.collected = True
                    self.key_collected = True  # Marcar como obtenida

                # La puerta técnicamente siempre está abierta (self.door.open = True)
                # pero verificamos que tenga la llave para poder usarla
                if (self.key_collected and
                        self.hitbox.colliderect(current_level.door.rect)):
                    current_level.door.open = True  # Redundante por claridad
                    # Lógica para cambiar de nivel [...]

            # Recolección de powerups
            for powerup in current_level.powerups[:]:
                if self.hitbox.colliderect(powerup.rect):
                    if self.store_powerup(powerup):
                        current_level.powerups.remove(powerup)

            # Actualización de animación
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
            self.bombs.append(Bomb(grid_x * TILE_SIZE, grid_y * TILE_SIZE, self, False, self.base_explosion_range, 3))
            self.available_bombs -= 1  # Consumir bomba

    def take_damage(self, amount):
        # Verificar protección contra daño
        if self.invincible:
            return False

        if self.item_effects.get("has_shield", False):
            self.item_effects["has_shield"] = False
            self.invincible = True
            self.invincible_frames = self.invincible_duration
            return False

        if self.active_effects.get("bomb_immune", False):
            return False

        # Aplicar daño
        self.lives -= amount
        self.invincible = True
        self.invincible_frames = self.invincible_duration

        # Manejar muerte
        if self.lives <= 0:
            revive_chance = self.item_effects.get("revive_chance", 0)
            if random.random() < revive_chance:
                self.lives = 1
                return False
            return True  # Jugador murió
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

    def draw_items(self, surface):
        """Dibuja los ítems activos en la esquina superior derecha"""
        x_pos = WIDTH - 40
        y_pos = 10

        # Dibujar título
        title = DEFAULT_FONT.render("Ítems:", True, WHITE)
        surface.blit(title, (x_pos - 100, y_pos))

        # Dibujar ítems
        for i, item in enumerate(self.permanent_items):
            if item['surface']:
                surface.blit(item['surface'], (x_pos, y_pos + 30 + i * 40))




    def draw(self, surface):
        if not self.visible:
            return

        try:
            draw_rect = self.rect
            # Para walk: frame_index entero (0-1-2)
            if self.current_animation == "walk":
                frame_index = int(self.animation_frame) % 3
            # Para idle: frame_index puede ser float para transiciones suaves
            else:
                frame_index = int(self.animation_frame) % len(self.animations["idle"][self.facing])

            current_frame = self.animations[self.current_animation][self.facing][frame_index]
            surface.blit(current_frame, draw_rect)



        except Exception as e:
            print(f"Error dibujando: {e}")
            pygame.draw.rect(surface, self.color, self.rect)

        self.weapon.draw(surface)
