import sys
import pygame

from modules import boss
from modules.boss import Boss
from modules.interlevelscreen import InterLevelScreen
from modules.powerups import Powerup
from modules.button import Button
from modules.level import Level
from modules.player import Player
from modules.utils import GameState, Difficulty, GRAY, GREEN, RED, BLUE, BLACK, HEIGHT, WIDTH, TILE_SIZE, FPS, WHITE, ScrollingBackground

'''

Boss Fight      
#Bomb Lord:
#Coloca 5 bombas en posiciones aleatorias
#Puede invertir los controles del jugador
#No puedes poner bombas por 5 segundos
#Super bombas que explotan en un rango de todo el mapa
#Embestida, luego de esta queda cansado
class Boss_Fight:

Ambientacion
#Oscuridad
#Trampas de hielo
#Trampa venenosa
#Trampa de fuego
#Hoyo en el que el jugador cae al spawn
#Trampa que invierte el movimiento del jugador
#class Traps:


Pantalla de configuraciones
Pantalla con los mejores puntajes
Pantalla de información
Ajustar pantalla completa
Ajustar resolucion
Tiempo de invulnerabilidad al iniciar un mundo
Animacion de inicio del juego
Animacion explosiones
Armas
Musica

'''
# Inicialización de Pygame
pygame.init()
if not pygame.font.get_init():  # Verifica si el módulo de fuentes está inicializado
    pygame.font.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomb's Before")
info = pygame.display.Info()

real_width, real_height = info.current_w, info.current_h

from modules.utils import load_fonts
DEFAULT_FONT = load_fonts(20)
TITLE_FONT = load_fonts(30)

if DEFAULT_FONT is None or TITLE_FONT is None:
    print("¡Error: No se pudo cargar ninguna fuente!")
    pygame.quit()
    sys.exit()


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.levels = [
            Level(1, Difficulty.EASY, self),
            Level(2, Difficulty.MEDIUM, self),
            Level(3, Difficulty.HARD, self),
            Level(4, Difficulty.FINAL_BOSS, self)
        ]
        self.current_level_index = 0
        self.player = None
        self.score = 0
        self.start_time = 0
        #self.font = custom
        self.background = ScrollingBackground("assets/textures/bg/background.png")

        # Botones del menú
        self.start_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2, 200, 50,
            "COMENZAR", GRAY, (100, 255, 100), font=DEFAULT_FONT)

        # Botones de selección de personaje
        self.character_buttons = [
            Button(
                WIDTH // 4 - 75, HEIGHT // 2 + 100, 150, 50,
                "BOMBER", BLUE, (100, 100, 255), font=DEFAULT_FONT),
            Button(
                WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 50,
                "TANKY", GREEN, (100, 255, 100), font=DEFAULT_FONT),
            Button(
                3 * WIDTH // 4 - 75, HEIGHT // 2 + 100, 150, 50,
                "PYRO", (255, 0, 0), (255, 100, 100), font=DEFAULT_FONT)]
            #Button(
                #3 * WIDTH // 4 - 75, HEIGHT // 2 + 100, 150, 50,
                #"CLERIC", (255, 0, 0), (255, 100, 100))
        #]

        # Textos descriptivos de personajes
        self.character_descriptions = [
            ["Vida: 3", "Velocidad: 3", "Bombas: 3"],
            ["Vida: 5", "Velocidad: 2", "Bombas: 2"],
            ["Vida: 2", "Velocidad: 4", "Bombas: 4"],
            #["Vida: 2", "Velocidad: 2", "Bombas: 2"]
        ]

        self.interlevel_screen = None
        self.spinning_roulette = False
        self.item_selected = None


        try:
            self.title_image = pygame.image.load("assets/textures/bg/title2.png").convert_alpha()
            self.title_image = pygame.transform.smoothscale(self.title_image, (408, 612))  # Ajusta el tamaño
            self.title_rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        except:
            self.title_image = None

        self.frozen_enemies = False  # Para control global

    def start_game(self, character_type):
        self.levels = [
            Level(0, Difficulty.EASY, self),
            Level(1, Difficulty.MEDIUM, self),
            Level(2, Difficulty.HARD, self),
            Level(3, Difficulty.FINAL_BOSS, self)]
        self.current_level_index = 3

        # Crear jugador según el tipo seleccionado
        if character_type == 0:  # Bomber
            self.player = Player(1, 1, 99, 15, BLUE, 51, 0,  self )
        elif character_type == 1:  # Tanky
            self.player = Player(1, 1, 5, 2, GREEN, 3, 1,  self)
        elif character_type == 2:  # Pyro
            self.player = Player(1, 1, 2, 5, RED, 8, 2,  self)
        elif character_type == 3: #Cleric
            self.player = Player(1, 1, 2, 4, WHITE, 4, 3,  self)

        self.ensure_starting_position()
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.state = GameState.GAME


    def ensure_starting_position(self):
        """Garantiza que el área inicial esté despejada"""
        current_level = self.levels[self.current_level_index]
        safe_zone = [
            (1, 1), (1, 2), (2, 1), (2, 2),
            (1, 3), (3, 1), (2, 3), (3, 2)
        ]

        # Eliminar bloques en zona segura
        current_level.map = [
            b for b in current_level.map
            if not any(
                b.rect.x == x * TILE_SIZE and
                b.rect.y == y * TILE_SIZE
                for x, y in safe_zone
            )
        ]

    def between_levels(self):
        """Transición al siguiente nivel con reinicio de estados"""
        # 1. Cambiar estado y crear pantalla de selección
        if self.state == GameState.INTERLEVEL:
            return
        self.state = GameState.INTERLEVEL
        self.interlevel_screen = InterLevelScreen(self.player)


    def prepare_next_level(self):
        # 2. Verificar si es el último nivel
        current_level = self.levels[self.current_level_index]
        current_level.__init__(
            current_level.number,
            current_level.difficulty,
            self)

        # 4. Resetear propiedades del jugador
        self._reset_player_for_new_level()

        # 5. Limpiar efectos temporales
        self._clear_temporary_effects()

        self.ensure_starting_position()

        print(f"Level {self.current_level_index + 1} loaded, {len(self.levels)}")
        return True

    def _reset_player_for_new_level(self):
        """Reinicia propiedades del jugador para el nuevo nivel"""
        self.player.rect.x = TILE_SIZE
        self.player.rect.y = TILE_SIZE
        self.player.hitbox.x = self.player.rect.x + 5
        self.player.hitbox.y = self.player.rect.y + 5
        self.player.key_collected = False
        self.player.available_bombs = self.player.bomb_capacity  # Recargar bombas
        self.player.invincible = False
        self.player.visible = True

    def _clear_temporary_effects(self):
        """Limpia efectos que no deben persistir entre niveles"""
        self.player.active_effects = {
            "bomb_immune": False,
            "phase_through": False
        }
        self.frozen_enemies = False
        self.player.explosion_range = self.player.base_explosion_range
        self.player.weapon.damage = self.player.weapon.base_damage
        self.player.weapon.speed = 10



    def _handle_skip_choice(self):
        if not self.prepare_next_level():
            self.state = GameState.VICTORY
        else:
            self.state = GameState.GAME
        return True

    def _handle_stat_choice(self, choice):
        self.apply_choice(choice)
        if not self.prepare_next_level():
            self.state = GameState.VICTORY
        else:
            self.state = GameState.GAME
        return True

    def _handle_item_choice(self, effect_name):
        self.player.apply_item_effect(effect_name)
        if not self.prepare_next_level():
            self.state = GameState.VICTORY
        else:
            self.state = GameState.GAME
        return True

    def apply_choice(self, choice: int):
        """Aplica la mejora de estadística seleccionada"""
        stat_boost = {
            0: ("bomb_capacity", 1),
            1: ("lives", 1),
            2: ("speed", 1),
            3: ("damage", 1)
        }

        stat, amount = stat_boost[choice]
        current_value = getattr(self.player, stat)
        setattr(self.player, stat, current_value + amount)

        # Caso especial para bombas
        if choice == 0:
            self.player.available_bombs = self.player.bomb_capacity

    def apply_item_effect(self, effect_name: str):
        """Aplica el efecto de un ítem especial"""
        effect_mapping = {
            "speed_boost": lambda: setattr(self.player, "speed", self.player.speed * 1.5),
            "homing_bullets": lambda: setattr(self.player.weapon, "homing", True),
            "shotgun": lambda: setattr(self.player.weapon, "spread_shot", True),
            "bullet_heal": lambda: setattr(self.player, "bullet_heal_counter", 0),
            "has_shield": lambda: setattr(self.player, "has_shield", True),
            "double_damage": self._apply_double_damage,
            "revive_chance": lambda: setattr(self.player, "revive_chance", 0.25),
            "indestructible_bomb": lambda: setattr(self.player, "bomb_pierces_indestructible", True)
        }

        if effect_name in effect_mapping:
            effect_mapping[effect_name]()

    def _apply_double_damage(self):
        """Efecto especial para el ítem de doble daño"""
        self.player.damage += 5
        self.player.enemy_damage_multiplier = 2.0


    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.USEREVENT + 10:  # BOMB_IMMUNITY
                self.player.active_effects["bomb_immune"] = False
            elif event.type == pygame.USEREVENT + 11:  # PHASE_TROUGH
                self.player.active_effects["phase_through"] = False
            elif event.type == pygame.USEREVENT + 12:  # FREEZE_ENEMIES
                self.frozen_enemies = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
                if event.button == 1:
                    if self.state == GameState.INTERLEVEL:
                        choice = self.interlevel_screen.get_choice(mouse_pos, mouse_click)
                        print(f"Choice returned: {choice}")
                        if not choice:
                            return True
                        if choice["type"] == "skip":

                            self.current_level_index += 1
                            return self._handle_skip_choice()
                        elif choice["type"] == "stat":

                            self.current_level_index += 1
                            return self._handle_stat_choice(choice["value"])
                        elif choice["type"] == "item":

                            self.current_level_index += 1
                            return self._handle_item_choice(choice["effect"])


                        self.prepare_next_level()
                        self.state = GameState.GAME

            if event.type == pygame.KEYDOWN:
                if self.state == GameState.GAME and event.key == pygame.K_SPACE:
                    self.player.activate_powerup()
                elif event.type == pygame.USEREVENT + 10:
                    self.player.active_effects["bomb_inmune"] = False

                if self.state == GameState.GAME and event.key == pygame.K_e:
                    self.player.player_place_bomb()

                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU




        keys = pygame.key.get_pressed()
        if self.state == GameState.GAME:
            if keys[pygame.K_UP]:
                self.player.shoot("up")
            elif keys[pygame.K_DOWN]:
                self.player.shoot("down")
            elif keys[pygame.K_LEFT]:
                self.player.shoot("left")
            elif keys[pygame.K_RIGHT]:
                self.player.shoot("right")


        # Manejo de botones según el estado del juego
        if self.state == GameState.MENU:
            self.start_button.check_hover(mouse_pos)
            if self.start_button.is_clicked(mouse_pos, mouse_click):
                self.state = GameState.CHARACTER_SELECT

        elif self.state == GameState.CHARACTER_SELECT:
            for i, button in enumerate(self.character_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click):
                    self.start_game(i)

        elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
            if mouse_click:
                self.state = GameState.MENU

        """Maneja eventos en la pantalla entre niveles"""




        return True

    def update(self):
        if self.state != GameState.GAME or not self.player:
            return



        current_level = self.levels[self.current_level_index]
        self.player.update_phase_effect(current_level)
        keys = pygame.key.get_pressed()

        if current_level.difficulty == Difficulty.FINAL_BOSS:
            if len(current_level.enemies) == 0:  # Asumiendo que el jefe es el único enemigo
                self.state = GameState.VICTORY

        if current_level.difficulty != Difficulty.FINAL_BOSS:
            if current_level.door.open and self.player.hitbox.colliderect(current_level.door.rect):
                self.between_levels()
                current_level.update_boss_powerups()


        # Movimiento del jugador
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        self.player.move(dx, dy, current_level.map, current_level)

        for enemy in current_level.enemies[:]:
            if isinstance(enemy, Boss):  # Comportamiento especial para el jefe
                enemy.update(
                    player=self.player,
                    current_time=pygame.time.get_ticks(),
                    arena_blocks=current_level.map
                )
            else:  # Comportamiento normal para enemigos
                enemy.update(current_level.map)

        self.player.update_weapon(current_level)

        for bullet in self.player.weapon.bullets[:]:
            bullet.update(current_level)

        for bomb in self.player.bombs[:]:
            if bomb.update(current_level):
                current_level.check_bomb_collisions(bomb, self.player)
                self.player.bombs.remove(bomb)

        for enemy in current_level.enemies:
            if (enemy.state != "dead" and
                    self.player.hitbox.colliderect(enemy.rect) and
                    not self.player.invincible):

                base_damage = 1
                damage = int(base_damage * self.player.enemy_damage_multiplier)
                self.player.take_damage(damage)
                if self.player.take_damage(damage):
                    self.player.update_invincibility()

            if self.player.lives <= 0:
                self.state = GameState.GAME_OVER
                return
        if current_level.difficulty == Difficulty.FINAL_BOSS:
            for enemy in current_level.enemies:
                if isinstance(enemy, Boss):
                    for bomb in enemy.boss_bombs[:]:
                        if bomb.update(current_level):
                            current_level.check_bomb_collisions(bomb, self.player)
                            enemy.boss_bombs.remove(bomb)

        if current_level.difficulty != Difficulty.FINAL_BOSS:
            if (hasattr(current_level, 'key') and
                    current_level.key.revealed and
                    not current_level.key.collected and
                    self.player.hitbox.colliderect(current_level.key.rect)):

                    current_level.key.collected = True
                    self.player.key_collected = True
                    current_level.open_door()

            if current_level.door.open and self.player.hitbox.colliderect(current_level.door.rect):
                self.between_levels()
                self.score += 500





    def draw(self):
        window.fill(BLACK)

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.CHARACTER_SELECT:
            self.draw_character_select()
        elif self.state == GameState.GAME:
            self.draw_game()
        elif self.state == GameState.INTERLEVEL:
            self.interlevel_screen.draw(window)
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_victory()


        pygame.display.flip()

    def draw_menu(self):
        self.background.update()
        self.background.draw(window)
        if self.title_image:
            window.blit(self.title_image, self.title_rect)
        else:
            title = TITLE_FONT.render("BOMB'S BEFORE", True, WHITE)
            window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        self.start_button.draw(window)

    def draw_character_select(self):
        title = TITLE_FONT.render("SELECCIONA TU PERSONAJE", True, WHITE)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        # Dibujar botones de personajes
        for button in self.character_buttons:
            button.draw(window)

        # Dibujar descripciones de personajes sin superposición
        for i, desc_lines in enumerate(self.character_descriptions):
            x_pos = self.character_buttons[i].rect.x
            y_pos = self.character_buttons[i].rect.y - 10 - len(desc_lines) * 25

            for j, line in enumerate(desc_lines):
                text = DEFAULT_FONT.render(line, True, WHITE)
                window.blit(text, (x_pos, y_pos + j * 25))

    def draw_game(self):
        current_level = self.levels[self.current_level_index]

        # Dibujar mapa
        for block in current_level.map:
            if not block.destroyed:
                block.draw(window)

        # Dibujar puerta y llave
        if current_level.difficulty != Difficulty.FINAL_BOSS:
            current_level.door.draw(window)
            if current_level.key and not current_level.key.collected and current_level.key.revealed:
                current_level.key.draw(window)

        # Dibujar enemigos
        for enemy in current_level.enemies:
            enemy.draw(window)

        # Dibujar bombas
        for bomb in self.player.bombs:
            bomb.draw(window)

        for powerup in current_level.powerups:
            powerup.draw(window)


        # Dibujar jugador
        self.player.draw(window)
        # Dibujar HUD
        lives_text = DEFAULT_FONT.render(f"Vidas: {self.player.lives}", True, WHITE)
        score_text = DEFAULT_FONT.render(f"Puntos: {self.score}", True, WHITE)
        level_text = DEFAULT_FONT.render(
            f"Nivel: {self.current_level_index + 1}/{len(self.levels)}",
            True, WHITE)
        bombs_text = DEFAULT_FONT.render(
            f"Bombas: {self.player.available_bombs}/{self.player.bomb_capacity}",
            True, WHITE)

        window.blit(lives_text, (10, 10))
        window.blit(score_text, (10, 50))
        window.blit(level_text, (WIDTH - 150, 10))
        window.blit(bombs_text, (WIDTH - 150, 50))

        # Mostrar si tiene la llave
        key_text = DEFAULT_FONT.render(
            "Llave: " + ("Sí" if self.player.key_collected else "No"),
            True, WHITE)
        window.blit(key_text, (WIDTH // 2 - key_text.get_width() // 2, 10))

        if self.player.stored_powerup:
            powerup_sprite = Powerup._sprites[self.player.stored_powerup.type]
            powerup_sprite = pygame.transform.scale(powerup_sprite, (32, 32))
            window.blit(powerup_sprite, (WIDTH - 50, HEIGHT - 50))

            # Texto descriptivo



    def draw_game_over(self):
        text = DEFAULT_FONT.render("GAME OVER", True, RED)
        score = DEFAULT_FONT.render(f"Puntuación final: {self.score}", True, WHITE)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
        window.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 + 20))

        restart = DEFAULT_FONT.render("Haz clic para volver al menú", True, WHITE)
        window.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 80))

    def draw_victory(self):
        text = DEFAULT_FONT.render("¡VICTORIA!", True, GREEN)
        score = DEFAULT_FONT.render(f"Puntuación final: {self.score}", True, WHITE)

        play_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = DEFAULT_FONT.render(f"Tiempo: {play_time} segundos", True, WHITE)

        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
        window.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 20))
        window.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 40))

        restart = DEFAULT_FONT.render("Haz clic para volver al menú", True, WHITE)
        window.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 100))

    Powerup.load_sprites()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            running = self.handle_events()
            self.update()
            if self.state == GameState.GAME:
                self.player.update_invincibility()
            self.draw()
            fps = clock.get_fps()
            pygame.display.set_caption(f"BomberMan | FPS: {fps:.1f}")
            clock.tick(FPS)



if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()