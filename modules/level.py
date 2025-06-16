from modules.powerups import Powerup
from modules.utils import Difficulty, TILE_SIZE
import random
from modules.enemy import Enemy
from modules.block import Block
from modules.door import Door, Key

class Level:
    def __init__(self, number, difficulty):
        self.number = number
        self.difficulty = difficulty
        self.map = []
        self.door = None
        self.key = None
        self.enemies = []
        self.door_block_position = None
        self.generate_level()
        self.powerups = []

    def generate_level(self):
        self.generate_map()
        self.generate_door()
        self.generate_enemies()

    def generate_map(self):
        width, height = 20, 15
        indestructible_prob = {
            Difficulty.EASY: 0.3,
            Difficulty.MEDIUM: 0.4,
            Difficulty.HARD: 0.5
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
        self.create_path_to_door(self.door_block_position, self.door_block_position)


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
                        if not (b.rect.x == path_x * TILE_SIZE and
                                b.rect.y == path_y * TILE_SIZE)
                    ]


                    # 50% de probabilidad de ser destructible
                    is_destructible = random.choice([True, False])
                    self.map.append(Block(path_x, path_y, destructible=is_destructible))

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
                                   TILE_SIZE and not b.destructible for b in self.map)

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
        self.create_path_to_door(door_x, door_y)

        # Generar la llave en un bloque destructible
        self.generate_key()

    def create_path_to_door(self, door_x, door_y):
        # Crear un camino de 3 bloques hacia la puerta
        directions = []
        if door_x == 0:  # Puerta izquierda
            directions = [(1, 0)]
        elif door_x == 19:  # Puerta derecha
            directions = [(-1, 0)]
        elif door_y == 0:  # Puerta arriba
            directions = [(0, 1)]
        elif door_y == 14:  # Puerta abajo
            directions = [(0, -1)]

        for dx, dy in directions:
            for i in range(1, 4):  # Crear camino de 3 bloques
                path_x = door_x + dx * i
                path_y = door_y + dy * i
                if 0 <= path_x < 20 and 0 <= path_y < 15:
                    # Eliminar cualquier bloque existente en esta posición
                    self.map = [b for b in self.map if
                                not (b.rect.x == path_x * TILE_SIZE and b.rect.y == path_y * TILE_SIZE)]
                    # Añadir bloque destructible (50% de probabilidad)
                    if random.random() < 0.5:
                        self.map.append(Block(path_x, path_y, destructible=True))

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
            self.key = Key(key_block.rect.x // TILE_SIZE, key_block.rect.y // TILE_SIZE)



    def generate_enemies(self):
        enemy_count = {
            Difficulty.EASY: 3,
            Difficulty.MEDIUM: 5,
            Difficulty.HARD: 7
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
                self.enemies.append(Enemy(x, y, enemy_type))

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

    def generate_powerup(self, x, y):
        powerup = Powerup(x, y)
        self.powerups.append(powerup)
        print(f"[DEBUG] Powerup generado: {powerup.type.name} en ({x}, {y})")

    def check_bomb_collisions(self, bomb, player):
        if not bomb.exploded:
            return
        # Destruir bloques
        blocks_to_remove = []
        for block in self.map[:]:
            if block.destructible and not block.destroyed:
                for exp_rect in bomb.explosion_rects:
                    if block.rect.colliderect(exp_rect):
                        block.destroyed = True
                        blocks_to_remove.append(block)
                        if random.random() <= 0.5:
                            self.generate_powerup(block.rect.x, block.rect.y)
                        if block.has_key and not block.revealed_key:
                            block.revealed_key = True
                            self.key.rect.x = block.rect.x
                            self.key.rect.y = block.rect.y
                            self.key.collected = False
                        break

        for block in blocks_to_remove:
            if block in self.map:
                self.map.remove(block)

        for exp_rect in bomb.explosion_rects:
            if player.hitbox.colliderect(exp_rect) and not player.invincible:
                player.lives -= 1
                player.take_damage()
                break


        # Dañar enemigos
        for enemy in self.enemies[:]:  # Usamos copia para poder modificar la lista
            if enemy.state != "dead":
                for exp_rect in bomb.explosion_rects:
                    if enemy.rect.colliderect(exp_rect):
                        enemy.take_damage()
                        if enemy.state == "dead":
                            self.enemies.remove(enemy)
                        break

        print(f"[DEBUG] Bloques en mapa: {len(self.map)}")
        print(f"[DEBUG] Powerups activos: {len(self.powerups)}")

    def update_powerups(self, player):
        for powerup in self.powerups[:]:
            powerup.update()
            if not powerup.active:
                self.powerups.remove(powerup)
            elif player.rect.colliderect(powerup.rect):
                if player.store_powerup(powerup):
                    self.powerups.remove(powerup)
