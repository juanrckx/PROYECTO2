import os

import pygame
from utils import  TILE_SIZE, FPS

class Bomb:
    def __init__(self, x, y, player, is_super, explosion_range, timer=3):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.timer = timer * FPS  # Convertir segundos a frames
        self.explosion_range = explosion_range
        self.exploded = False
        self.explosion_timer = 30
        self.explosion_rects = []
        self.player = player
        self.is_super = is_super

        self.bombs_frames = self._load_gif_frames("bomb")
        self.explosion_frames = self._load_gif_frames("explosion")
        self.current_frame = 0
        self.bomb_animation_speed = 0.1
        self.explosion_animation_speed = 0.05
        self.last_update = pygame.time.get_ticks()

    def _load_gif_frames(self, frame_type):
        frames = []
        folder_path = "assets/textures/materials/bomb/"

        prefix = f"{frame_type}_"
        frame_files = sorted(
            [f for f in os.listdir(folder_path) if f.startswith(prefix)],
            key=lambda x: int(x.split('_')[1].split('.')[0])
        )

        for file in frame_files:
                frame = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
                frame = pygame.transform.scale(frame, (TILE_SIZE, TILE_SIZE))
                frames.append(frame)


        return frames

    def update(self, current_level = None):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.bomb_animation_speed * 1000:  # Convierte segundos a milisegundos
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.bombs_frames)

        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0 and current_level is not None:
                self.explode(self.player, current_level)
                return False
        else:
            self.explosion_timer -= 1
        return self.explosion_timer <= 0



    def explode(self, player, current_level):
        self.exploded = True
        self.explosion_rects = [self.rect.copy()]

        # Definir patrones de explosión
        base_pattern = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if hasattr(player, 'get_explosion_pattern') and player.get_explosion_pattern() == "diamond":
            base_pattern.extend([(1, 1), (-1, 1), (1, -1), (-1, -1), (2, 0), (0, 2), (-2, 0), (0, -2)])

        for dx, dy in base_pattern:
            for i in range(1, self.explosion_range + 1):
                new_rect = pygame.Rect(
                    self.rect.x + dx * i * TILE_SIZE,
                    self.rect.y + dy * i * TILE_SIZE,
                    TILE_SIZE, TILE_SIZE
                )

                # Solo verificar colisión si NO tenemos indestructible_bomb
                if hasattr(player, 'item_effects') and not player.item_effects.get("indestructible_bomb"):
                    if any(not block.destructible and block.rect.colliderect(new_rect)
                           for block in current_level.map):
                        break

                self.explosion_rects.append(new_rect)

    def draw(self, surface):
        if not self.exploded:
            frame = self.bombs_frames[self.current_frame]
            surface.blit(frame, self.rect)
        else:
            # Debug: verificar si hay rectángulos
            print(f"Dibujando explosión. Rects: {len(self.explosion_rects)}, Frames: {len(self.explosion_frames)}")

            if not self.explosion_rects or not self.explosion_frames:
                return

            frame_index = min(int((1 - self.explosion_timer / 30) * len(self.explosion_frames)),
                              len(self.explosion_frames) - 1)
            explosion_frame = self.explosion_frames[frame_index]

            for exp_rect in self.explosion_rects:
                # Asegurar que el frame tenga tamaño válido
                if explosion_frame.get_size() == (0, 0):
                    print("¡Frame de explosión inválido!")
                    continue

                try:
                    scaled_rect = exp_rect.inflate(20, 20)
                    scaled_frame = pygame.transform.scale(explosion_frame, scaled_rect.size)
                    surface.blit(scaled_frame, scaled_rect)
                except:
                    print("¡Error al dibujar explosión!")