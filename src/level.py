import pygame
import random

from boss import Boss
from powerups import Powerup
from utils import Difficulty, TILE_SIZE, PowerupType, WIDTH, HEIGHT
from enemy import Enemy
from block import Block
from door import Door, Key


class Level:
    def __init__(self, number, difficulty, game):

        self.number = number
        self.difficulty = difficulty
        self.game = game
        self.map = []
        self.door = None
        self.key = None
        self.enemies = []
        self.door_block_position = None
        self.powerups = []
        self.generate_level()
        self.powerup_spawn_count = {"EXTRA_LIFE": 0,
            "EXTRA_BOMB": 0,
            "EXTRA_VELOCITY": 0,
            "EXTRA_DAMAGE": 0,
            "EXPLOSION_RANGE": 0,}
        self.last_powerup_timer = 0

    def generate_level(self):

        # Resetear contenido
        self.map = []
        self.enemies = []
        self.powerups = []
        self.player_spawn = (1, 1)




        if self.difficulty == Difficulty.TRANSITION_ROOM:
            self._generate_transition_room()

        elif self.difficulty == Difficulty.FINAL_BOSS:
            self._generate_boss_arena()

        else:
            self.generate_map()
            self.generate_door()
            self.generate_enemies()


    def generate_map(self):
        width, height = 20, 15
        indestructible_prob = {
            Difficulty.EASY: 0.3,
            Difficulty.MEDIUM: 0.4,
            Difficulty.HARD: 0.4
        }.get(self.difficulty, 0.4)

        safe_zone = [(1,1, (1,2,),(2,1), (2,2),(1,3), (3,1))]
        # Primero generamos todos los bloques normalmente
        for x in range(width):
            for y in range(height):
                if x in (0, width - 1) or y in (0, height - 1):
                    self.map.append(Block(x, y, destructible=False))

                elif (x, y) in safe_zone:
                    continue

                else:
                    # Bloques internos pueden ser destructibles o indestructibles
                    if random.random() < indestructible_prob:
                        if not self.would_trap_player(x, y, safe_zone):
                            self.map.append(Block(x, y, destructible=random.choice([True, False])))

            escape_routes = [(2,3), (3,2)]
            for j, k in escape_routes:
                self.map = [b for b in self.map if not (b.rect.x == j * TILE_SIZE and b.rect.y == k * TILE_SIZE)]

        self.ensure_door_access()
        #self.would_trap_player(10, 10, safe_zone)

    def _generate_transition_room(self):
        """Genera una sala del tamaño normal (20x15) con características especiales"""
        # Generar mapa básico como un nivel normal
        width, height = 20, 15
        for x in range(width):
            for y in range(height):
                if x in (0, width - 1) or y in (0, height - 1):
                    self.map.append(Block(x, y, destructible=False))

        # Posicionar puerta en el centro de la pared derecha (siempre abierta)
        door_x, door_y = width - 1, height // 2
        self.map = [b for b in self.map if not (b.rect.x == door_x * TILE_SIZE and b.rect.y == door_y * TILE_SIZE)]
        self.door = Door(door_x, door_y)
        self.door.open = True  # Puerta siempre abierta

        self.key = None

        # Generar powerups especiales (solo vida y bombas)
        powerup_positions = [
            (width // 3, height // 3),
            (2 * width // 3, height // 3),
            (width // 3, 2 * height // 3),
            (2 * width // 3, 2 * height // 3)
        ]

        for x, y in powerup_positions:
            powerup = Powerup(x * TILE_SIZE, y * TILE_SIZE)
            # Forzar tipo de powerup (50% vida, 50% bombas)
            powerup.type = random.choice([PowerupType.EXTRA_LIFE, PowerupType.EXTRA_BOMB])
            self.powerups.append(powerup)

        # Spawn del jugador cerca de la pared izquierda
        self.player_spawn = (2, height // 2)

    def _generate_boss_arena(self):
        # En level.py, modifica _generate_boss_arena
        """Generación corregida de la arena con sala de spawn y pasillo"""
        self.map = []
        self.enemies = []
        width, height = 20, 15

        # Paredes exteriores
        for x in range(width):
            for y in range(height):
                if x in (0, width - 1) or y in (0, height - 1):
                    self.map.append(Block(x, y, destructible=False))

        # Posicionar al jefe en el centro
        boss_x, boss_y = (width // 2) - 1, (height // 2) - 1

        # Posición de spawn del jugador (esquina superior izquierda)
        self.player_spawn = ((width // 2) - 1, (height // 2) - 1)
        boss = Boss(boss_x * TILE_SIZE, boss_y * TILE_SIZE)
        boss.set_level(self)
        self.enemies.append(boss)



    def ensure_door_access(self):
        """Garantiza que haya al menos un camino a la puerta"""
        if not self.door_block_position:
            return

        door_x, door_y = self.door_block_position
        directions = []

        # Determinar dirección para crear camino según posición de puerta
        if door_x == 0:  # Puerta izquierda
            directions = [(1, 0)]  # Derecha
        elif door_x == 19:  # Puerta derecha
            directions = [(-1, 0)]  # Izquierda
        elif door_y == 0:  # Puerta arriba
            directions = [(0, 1)]  # Abajo
        elif door_y == 14:  # Puerta abajo
            directions = [(0, -1)]  # Arriba

        # Crear camino de 3 bloques de largo hacia la puerta
        for dx, dy in directions:
            for i in range(1, 4):
                path_x = door_x + dx * i
                path_y = door_y + dy * i

                # Si está dentro de los límites
                if 1 <= path_x < 19 and 1 <= path_y < 14:
                    # Eliminar cualquier bloque existente en esta posición
                    self.map = [
                        b for b in self.map
                        if not (b.rect.x // TILE_SIZE == path_x and
                                b.rect.y // TILE_SIZE == path_y)
                    ]

                    # Crear un bloque destructible (para que siempre se pueda abrir camino)
                    self.map.append(Block(path_x, path_y, destructible=True))

    def would_trap_player(self, x, y, safe_zone):
        trap_patterns = ([(x, y), (x + 1, y), (x, y + 1)], [(x,y), (x - 1,y), (x, y - 1)], #Patron L
                         [(x, y), (x + 1, y), ( x - 1, y), (x, y + 1)], # Patron U
                         [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]) #Patron de esquinas

        for pattern in trap_patterns:
            all_blocks_indestructible = True
            for px, py in pattern:
                if (px, py) in safe_zone:
                    all_blocks_indestructible = False
                    break

                block_exists = any(b.rect.x == px * TILE_SIZE and b.rect.y == py *
                                   TILE_SIZE for b in self.map)

                if not block_exists and (px, py) != (x, y):
                    all_blocks_indestructible = False
                    break

            if all_blocks_indestructible:
                return True

        return False


    def generate_door(self):
        door_positions = [(0, 7), (19, 7), (10, 0), (10, 14)]
        door_x, door_y = random.choice(door_positions)
        self.door = Door(door_x, door_y)
        self.door_block_position = (door_x, door_y)

        # Generar camino hacia la puerta
        self.ensure_door_access()

        # Generar la llave en un bloque destructible
        self.generate_key()



    def open_door(self):
        if self.door_block_position:
            door_x, door_y = self.door_block_position
            # Buscar y eliminar el bloque en la posición de la puerta
            for i, block in enumerate(self.map):
                if (block.rect.x == door_x * TILE_SIZE and
                        block.rect.y == door_y * TILE_SIZE):
                    del self.map[i]
                    break
        self.door.open = True

    def generate_key(self):
        # Colocar la llave en un bloque destructible aleatorio
        destructible_blocks = [b for b in self.map if b.destructible]
        if destructible_blocks:
            key_block = random.choice(destructible_blocks)
            key_block.has_key = True
            key_block.revealed_key = False
            self.key = Key(key_block.rect.x // TILE_SIZE, key_block.rect.y // TILE_SIZE)




    def generate_enemies(self):
        enemy_count = {
            Difficulty.EASY: 3,
            Difficulty.MEDIUM: 5,
            Difficulty.HARD: 10
        }.get(self.difficulty, 3)

        self.enemies = []
        attempts = 0
        max_attempts = 100

        while len(self.enemies) < enemy_count and attempts < max_attempts:
            attempts += 1
            x, y = self.find_valid_position()

            if not any(block.rect.collidepoint(x * TILE_SIZE + TILE_SIZE // 2,
                                               y * TILE_SIZE + TILE_SIZE // 2)
                       for block in self.map if not block.destroyed):
                enemy_type = random.choices([1, 2, 3], weights=[0.5, 0.3, 0.2])[0]
                self.enemies.append(Enemy(x, y, enemy_type, self.game))

    def find_valid_position(self):
        while True:
            x = random.randint(1, 18)
            y = random.randint(1, 13)

            # Verificar que no haya bloque indestructible
            blocked = any(
                block.rect.collidepoint(x * TILE_SIZE, y * TILE_SIZE)
                for block in self.map
                if not block.destructible and not block.destroyed
            )

            # Verificar que no haya otro enemigo cerca
            enemy_near = any(
                abs(enemy.rect.x // TILE_SIZE - x) < 2 and
                abs(enemy.rect.y // TILE_SIZE - y) < 2
                for enemy in self.enemies
            )

            if not blocked and not enemy_near:
                return x, y

    def is_border_block(self, block):
        """Verifica si un bloque es parte del borde indestructible del mapa"""
        return (block.rect.x <= 0 or
                block.rect.y <= 0 or
                block.rect.x >= (19 * TILE_SIZE) or  # 20 columnas (0-19)
                block.rect.y >= (14 * TILE_SIZE))  # 15 filas (0-14)

            # Actualizar bombas
    def check_bomb_collisions(self, bomb, player):
        if not bomb.exploded:
            bomb.explode(self)
        player_hit = False
        if bomb.exploded:
            for block in self.map[:]:
                if block.destructible and not block.destroyed:
                    for exp_rect in bomb.explosion_rects:
                        if block.rect.colliderect(exp_rect):
                            block.destroyed = True
                            self.map.remove(block)
                            if random.random() <= 0.7 and len(self.powerups) < 5:
                                self.powerups.append(Powerup(block.rect.x, block.rect.y))

                            if (getattr(block, 'has_key') and
                                    block.has_key and not block.revealed_key):
                                self.key.rect.x = block.rect.x
                                self.key.rect.y = block.rect.y
                                self.key.collected = False
                                self.key.revealed = True
                            if not (hasattr(block, 'has_key') and block.has_key):
                                if block in self.map:
                                    self.map.remove(block)

                            break

            for exp_rect in bomb.explosion_rects:
                if not player_hit and player.hitbox.colliderect(
                        exp_rect) and not player.invincible and not player.active_effects.get("bomb_immune", False):
                    player_hit = True
                    player.take_damage(amount=1)
                    break

            for enemy in self.enemies[:]:  # Usamos copia para poder modificar la lista
                if enemy.state != "dead":
                    for exp_rect in bomb.explosion_rects:
                        if enemy.rect.colliderect(exp_rect):
                            enemy.take_damage(amount=2)

            if bomb.exploded:
                if hasattr(player, 'item_effects') and player.item_effects.get("indestructible_bomb"):
                    for exp_rect in bomb.explosion_rects:
                        if block.rect.colliderect(exp_rect):
                            if exp_rect.x == 0 or exp_rect.x == WIDTH - TILE_SIZE or exp_rect.y == 0 or exp_rect.y == HEIGHT - TILE_SIZE:
                                continue
                            block.destroyed = True
                            self.map.remove(block)
                            if random.random() <= 0.7 and len(self.powerups) < 5:
                                self.powerups.append(Powerup(block.rect.x, block.rect.y))
                            if (getattr(block, 'has_key') and
                                    block.has_key and not block.revealed_key):
                                self.key.rect.x = block.rect.x
                                self.key.rect.y = block.rect.y
                                self.key.collected = False
                                self.key.revealed = True
                            if not (hasattr(block, 'has_key') and block.has_key):
                                if block in self.map:
                                    self.map.remove(block)



    def generate_boss_powerup(self):
        if self.difficulty != Difficulty.FINAL_BOSS:
            return
        allowed_powerups = []  # Máx. 1 aparición

        if self.powerup_spawn_count.get("EXTRA_VELOCITY", 0) >= 3:
            allowed_powerups.append(PowerupType.EXTRA_VELOCITY)
        if self.powerup_spawn_count.get("EXTRA_DAMAGE", 0) >= 3:
            allowed_powerups.append(PowerupType.EXTRA_DAMAGE)
        if self.powerup_spawn_count.get("EXPLOSION_RANGE", 0) >= 1:
            allowed_powerups.append(PowerupType.EXPLOSION_RANGE)

        allowed_powerups.extend([PowerupType.EXTRA_LIFE, PowerupType.EXTRA_BOMB])

        if not allowed_powerups:
            return

        chosen_type = random.choice(allowed_powerups)
        x, y = self.find_valid_position()

        powerup = Powerup(x * TILE_SIZE, y * TILE_SIZE)
        powerup.type = chosen_type
        self.powerups.append(powerup)

        self.powerup_spawn_count[chosen_type.name] += 1


    def update_boss_powerups(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_powerup_timer > 15000:
            self.generate_boss_powerup()
            self.last_powerup_timer = current_time
