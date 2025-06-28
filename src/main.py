import math
import sys

import pygame
from traps import TrapManager
from boss import Boss
from button import Button
from interlevelscreen import InterLevelScreen
from level import Level
from player import Player
from powerups import Powerup
from utils import GameState, Difficulty, GRAY, GREEN, RED, BLUE, BLACK, HEIGHT, WIDTH, TILE_SIZE, FPS, WHITE, \
    ScrollingBackground, ScoreManager, SettingScreen, HighScoresScreen, ScrollableInfoScreen

'''


#TODO
Ambientacion
#Oscuridad
#Trampas de hielo
#Trampa venenosa
#Trampa de fuego
#Hoyo en el que el jugador cae al spawn
#Trampa que invierte el movimiento del jugador
#class Traps:

#TODO
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

PYRO 



#TODO

AUMENTAR PUNTAJE



'''
# Inicialización de Pygame
pygame.init()
if not pygame.font.get_init():  # Verifica si el módulo de fuentes está inicializado
    pygame.font.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomb's Before")
info = pygame.display.Info()

real_width, real_height = info.current_w, info.current_h

from utils import load_fonts
DEFAULT_FONT = load_fonts(20)
TITLE_FONT = load_fonts(30)

if DEFAULT_FONT is None or TITLE_FONT is None:
    pygame.quit()
    sys.exit()


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.last_state = self.state
        self.levels = [
            Level(1, Difficulty.EASY, self),
            Level(2, Difficulty.MEDIUM, self),
            Level(3, Difficulty.HARD, self),
            Level(4, Difficulty.TRANSITION_ROOM, self),
            Level(5, Difficulty.FINAL_BOSS, self)
        ]
        self.current_level_index = 0
        self.player = None
        self.score = 0
        self.score_multiplier = 1.0
        self.combo_counter = 0
        self.last_score_time = 0
        self.start_time = 0
        self.background = ScrollingBackground("assets/textures/bg/background.png")

        # Botones del menú
        self.start_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2, 200, 50,
            "COMENZAR", GRAY, (100, 255, 100), font=DEFAULT_FONT)
        self.settings_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50,
            "CONFIGURACIÓN", GRAY, (200, 200, 200), font=DEFAULT_FONT)

        self.records_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50,
            "RÉCORDS", GRAY, (200, 200, 200), font=DEFAULT_FONT)

        self.info_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50,
            "INFORMACIÓN", GRAY, (200, 200, 200), font=DEFAULT_FONT)

        # Variables para configuración
        self.settings = {
            "music_volume": 0.5,
            "sfx_volume": 0.7,
            "fullscreen": False,
        }

        # Datos de records
        self.high_scores = []  # Lista de tuplas (nombre, puntaje)

        # Cargar datos guardados

        # Botones de selección de personaje
        self.character_buttons = [
            Button(0, 0, 180, 60, "BOMBER", BLUE, (100, 100, 255), font=DEFAULT_FONT),
            Button(0, 0, 180, 60, "TANKY", GREEN, (100, 255, 100), font=DEFAULT_FONT),
            Button(0, 0, 180, 60, "PYRO", RED, (255, 100, 100), font=DEFAULT_FONT),
            Button(0, 0, 180, 60, "CLERIC", GRAY, (200, 200, 200), font=DEFAULT_FONT)
        ]

        # Textos descriptivos de personajes
        self.character_descriptions = [
            ["Vida: 5", "Velocidad: 4", "Bombas: 10"],
            ["Vida: 7", "Velocidad: 3", "Bombas: 8"],
            ["Vida: 3", "Velocidad: 5", "Bombas: 15"],
            ["Vida: 3", "Velocidad: 4", "Bombas: 10"]
        ]

        self.item_icons = {
            "bullet_heal": pygame.image.load(r"assets\textures\items\the_lovers.png").convert_alpha(),
            "has_shield": pygame.image.load(r"assets\textures\items\the_high_priestess.png").convert_alpha(),
            "shotgun": pygame.image.load(r"assets\textures\items\the_chariot.png").convert_alpha()
        }
        for key in self.item_icons:
            self.item_icons[key] = pygame.transform.scale(self.item_icons[key], (40, 40))

        self.character_items = {
            0: None,  # Bomber
            1: "has_shield",  # Tanky
            2: "bullet_heal",  # Pyro
            3: "shotgun"  # Cleric
        }

        self.interlevel_screen = None
        self.spinning_roulette = False
        self.item_selected = None
        self.current_music = None
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.music_tracks = {
            'menu': None,
            'game': None,
            'boss': None,
            'game_over': None,
            'interlevel': None
        }
        self.load_music()
        self.play_music("menu")

        self.score_manager = ScoreManager()
        self.settings_screen = SettingScreen()
        self.high_scores_screen = HighScoresScreen(self.score_manager)
        self.info_screen = ScrollableInfoScreen()



        self.title_image = pygame.image.load("assets/textures/bg/title2.png").convert_alpha()
        self.title_image = pygame.transform.smoothscale(self.title_image, (408, 612))  # Ajusta el tamaño
        self.title_rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))


        self.frozen_enemies = False  # Para control global
        self.level_start_time = 0



    def add_score(self, amount, combo=False):
        """Añade puntos al score con posible combo"""
        now = pygame.time.get_ticks()

        # Lógica de combo
        if combo:
            if now - self.last_score_time < 2000:  # 2 segundos para combo
                self.combo_counter += 1
                self.score_multiplier = min(3.0, 1.0 + self.combo_counter * 0.2)
            else:
                self.combo_counter = 0
                self.score_multiplier = 1.0
        else:
            self.combo_counter = 0
            self.score_multiplier = 1.0

        self.last_score_time = now
        self.score += int(amount * self.score_multiplier)

    def load_music(self):
        """Carga todos los archivos de música"""

        self.music_tracks = {
            'menu': pygame.mixer.Sound("assets/music/MENU.mp3"),
            'game': pygame.mixer.Sound("assets/music/GAME.mp3"),
            'boss': pygame.mixer.Sound("assets/music/BOSS.mp3"),
            'game_over': pygame.mixer.Sound("assets/music/GAMEOVER.mp3"),
            'interlevel': pygame.mixer.Sound("assets/music/VICTORY_INTERLEVEL.mp3"),
        }
        # Configurar volumen inicial
        for track in self.music_tracks.values():
            if track:
                track.set_volume(self.music_volume)


    def start_game(self, character_type):
        self.current_level_index = 0
        current_level = self.levels[self.current_level_index]
        self.level_start_time = pygame.time.get_ticks()

        # Crear jugador según el tipo seleccionado
        if character_type == 0:  # Bomber
            self.player = Player(1, 1, 5, 4, BLUE, 10, 0,  self )
        elif character_type == 1:  # Tanky
            self.player = Player(1, 1, 7, 3, GREEN, 8, 1,  self)
        elif character_type == 2:  # Pyro
            self.player = Player(1, 1, 3, 5, RED, 15, 2,  self)
        elif character_type == 3: #Cleric
            self.player = Player(1, 1, 3, 4, WHITE, 10, 3,  self)




        self.state = GameState.GAME
        if self.current_level_index < 3:
            self.score = 0
            self.start_time = pygame.time.get_ticks()
        current_level.generate_level()


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

        if self.current_level_index == 3:  # Índice del nivel del jefe
            self.player.can_place_bombs = False
            pygame.time.set_timer(pygame.USEREVENT + 40, 3000)
            boss_count = sum(1 for e in current_level.enemies if isinstance(e, Boss))
            if boss_count == 0:
                boss = Boss((20 // 2) - 1, (15 // 2) - 1)
                boss.set_level(current_level)
                current_level.enemies.append(boss)
            elif boss_count > 1:
                # Eliminar jefes adicionales
                current_level.enemies = [e for e in current_level.enemies
                                         if not isinstance(e, Boss)]
                current_level.enemies.append(Boss(8 * TILE_SIZE, 7 * TILE_SIZE))

        # 4. Resetear propiedades del jugador
        self._reset_player_for_new_level()


        # 5. Limpiar efectos temporales
        self._clear_temporary_effects()
        current_level.generate_level()
        current_level.ensure_starting_position()
        self.player.reset_item_effects()

        return True

    def _reset_player_for_new_level(self):
        """Reinicia propiedades del jugador para el nuevo nivel"""
        self.player.rect.x = TILE_SIZE
        self.player.rect.y = TILE_SIZE
        self.player.hitbox.x = self.player.rect.x + 5
        self.player.hitbox.y = self.player.rect.y + 5
        self.player.key_collected = False
        self.player.invincible = False
        self.player.visible = True
        self.player.can_place_bombs = True
        pygame.time.set_timer(pygame.USEREVENT + 20, 0)
        self.player.controls_inverted = False
        self.player.speed = self.player.base_speed
        self.player.ice_applied = False
        pygame.time.set_timer(pygame.USEREVENT + 50, 0)



    def _clear_temporary_effects(self):
        """Limpia efectos que no deben persistir entre niveles"""
        self.player.active_effects = {
            "bomb_immune": False,
            "phase_through": False
        }
        self.frozen_enemies = False
        self.player.explosion_range = self.player.base_explosion_range
        self.player.weapon.speed = 10
        self.player.weapon.damage = self.player.weapon.base_damage



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
        self.player.apply_item_effect(effect_name)

    def _apply_double_damage(self):
        """Efecto especial para el ítem de doble daño"""
        self.player.bullet.damage += 5
        self.player.bullet.base_damage += 5
        self.player.enemy_damage_multiplier = 2.0

    def play_music(self, track_name):
        """Reproduce una pista de música con transición suave"""
        if self.current_music == track_name:
            return

        # Detener música actual con fadeout
        if self.current_music and self.music_tracks.get(self.current_music):
            self.music_tracks[self.current_music].fadeout(500)

        # Reproducir nueva música
        new_track = self.music_tracks.get(track_name)
        if new_track:
            new_track.set_volume(self.music_volume)
            new_track.play(loops=-1)  # -1 para loop infinito
            self.current_music = track_name


    def set_music_volume(self, volume):
        """Ajusta el volumen de toda la música"""
        self.music_volume = max(0.0, min(1.0, volume))
        for track in self.music_tracks.values():
            if track:
                track.set_volume(self.music_volume)

    def stop_music(self):
        """Detiene toda la música"""
        pygame.mixer.stop()
        self.current_music = None


    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if self.state == GameState.INFO and event.type == pygame.MOUSEWHEEL:
                self.info_screen.handle_event(event)

            elif event.type == pygame.USEREVENT + 10:  # BOMB_IMMUNITY
                self.player.active_effects["bomb_immune"] = False
            elif event.type == pygame.USEREVENT + 11:  # PHASE_TROUGH
                self.player.active_effects["phase_through"] = False
            elif event.type == pygame.USEREVENT + 12:  # FREEZE_ENEMIES
                self.frozen_enemies = False

            if event.type == pygame.USEREVENT + 20:
                self.player.can_place_bombs = True
            if event.type == pygame.USEREVENT + 30:
                if self.player:
                    self.player.controls_inverted = False
            if event.type == pygame.USEREVENT + 40 :  # Fin del cooldown inicial
                self.player.can_place_bombs = True
                self.player.weapon = True
                if not Difficulty.TRANSITION_ROOM:
                    self.levels[self.current_level_index].enemies[0].can_attack = True

            if event.type == pygame.MOUSEMOTION:
                # Actualizar estado hover solo en estados relevantes
                if self.state == GameState.MENU:
                    self.start_button.check_hover(mouse_pos)
                    self.settings_button.check_hover(mouse_pos)
                    self.records_button.check_hover(mouse_pos)
                    self.info_button.check_hover(mouse_pos)
                elif self.state == GameState.CHARACTER_SELECT:
                    for button in self.character_buttons:
                        button.check_hover(mouse_pos)


            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
                if event.button == 1 and self.state == GameState.MENU:
                    if self.state == GameState.MENU:
                        if self.start_button.is_clicked(mouse_pos, mouse_click):
                            self.state = GameState.CHARACTER_SELECT

                        elif self.settings_button.is_clicked(mouse_pos, mouse_click):
                            self.state = GameState.SETTINGS

                        elif self.records_button.is_clicked(mouse_pos, mouse_click):
                            self.state = GameState.HIGHSCORES

                        elif self.info_button.is_clicked(mouse_pos, mouse_click):
                            self.state = GameState.INFO

                    elif self.state == GameState.SETTINGS:
                        result = self.settings_screen.handle_event(event)
                        if result == "back" and self.state == GameState.SETTINGS:
                            self.state = GameState.MENU

                    elif self.state == GameState.HIGHSCORES:
                        result = self.high_scores_screen.handle_event(event)
                        if result == "back" and self.state == GameState.HIGHSCORES:
                            self.state = GameState.MENU

                    elif self.state == GameState.INFO:
                        result = self.info_screen.handle_event(event)
                        if result == "back" and self.state == GameState.INFO:
                            self.state = GameState.MENU



                if self.state == GameState.INTERLEVEL:
                    if self.current_music != 'interlevel':
                        self.play_music('interlevel')
                    choice = self.interlevel_screen.get_choice(mouse_pos, mouse_click)
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
                    self.player.active_effects["bomb_immune"] = False

                if self.state == GameState.GAME and event.key == pygame.K_e and self.player.can_place_bombs:
                    self.player.player_place_bomb()

                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
            if event.type == pygame.USEREVENT + 50:
                self.player.speed = getattr(self.player, "original_speed", self.player.speed)
                self.player.ice_applied = False
                pygame.time.set_timer(pygame.USEREVENT + 50, 0)  # Cancelar el evento repetido





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

        elif self.state == GameState.CHARACTER_SELECT:
            for i, button in enumerate(self.character_buttons):
                button.check_hover(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click):
                    self.start_game(i)

            if self.settings_button.is_clicked(mouse_pos, mouse_click):
                self.state = GameState.SETTINGS

            self.records_button.check_hover(mouse_pos)
            if self.records_button.is_clicked(mouse_pos, mouse_click):
                self.state = GameState.HIGHSCORES

            self.info_button.check_hover(mouse_pos)
            if self.info_button.is_clicked(mouse_pos, mouse_click):
                self.state = GameState.INFO


        elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
            if mouse_click:
                self.state = GameState.MENU



        return True


    def update(self):
        if self.state != GameState.GAME or not self.player:
            return



        current_level = self.levels[self.current_level_index]
        self.player.update_phase_effect(current_level)
        keys = pygame.key.get_pressed()


        # Movimiento del jugador
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        self.player.move(dx, dy, current_level.map, current_level)
        #TrapManager.check_collision(player)



        for enemy in current_level.enemies[:]:
            if enemy.state == "dead" and not getattr(enemy, 'score_counted', False):
                base_score = 50 * (self.current_level_index + 1)
                self.add_score(base_score, combo=True)
                enemy.score_counted = True
            if isinstance(enemy, Boss):  # Comportamiento especial para el jefe
                enemy.update(
                    player=self.player,
                    arena_blocks=current_level.map
                )
            else:  # Comportamiento normal para enemigos
                enemy.update(self.player, current_level.map)

        self.player.update_weapon(current_level)

        for bullet in self.player.weapon.bullets[:]:
            bullet.update(current_level)

        for bomb in self.player.bombs[:]:
            if bomb.update(current_level):
                current_level.check_bomb_collisions(bomb, self.player)
                self.player.bombs.remove(bomb)

        for powerup in current_level.powerups[:]:
            if self.player.hitbox.colliderect(powerup.rect):
                self.add_score(20)

        for block in current_level.map[:]:
            if block.destroyed and not getattr(block, 'score_counted', False):
                self.add_score(10)
                block.score_counted = True


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

        for enemy in current_level.enemies:
            if isinstance(enemy, Boss):
                for bomb in enemy.boss_bombs[:]:
                    if bomb.update(current_level):
                        current_level.check_bomb_collisions(bomb, self.player)
                        enemy.boss_bombs.remove(bomb)

        if current_level.difficulty != Difficulty.FINAL_BOSS and current_level.difficulty != Difficulty.TRANSITION_ROOM:
            if (hasattr(current_level, 'key') and
                    current_level.key.revealed and
                    not current_level.key.collected and
                    self.player.hitbox.colliderect(current_level.key.rect)):

                    time_bonus = max(0, 1000 - (pygame.time.get_ticks() - self.level_start_time) // 100)
                    self.add_score(time_bonus)
                    current_level.key.collected = True
                    self.player.key_collected = True
                    current_level.open_door()

        if current_level.difficulty == Difficulty.TRANSITION_ROOM:
            current_level.open_door()

        if current_level.door.open and self.player.hitbox.colliderect(current_level.door.rect):
            self.between_levels()
            self.score += 500

        if hasattr(self, 'last_state') and self.last_state != self.state:
            self.handle_music_transition()
        self.last_state = self.state

        if (self.state == GameState.GAME and
                self.current_level_index == 4 and  # Nivel del jefe
                self.current_music != 'boss'):
            self.play_music('boss')

    def handle_music_transition(self):
        """Maneja los cambios de música según el estado del juego"""
        music_map = {
            GameState.MENU: 'menu',
            GameState.CHARACTER_SELECT: 'menu',
            GameState.GAME: 'game' if self.current_level_index < 4 else 'boss',
            GameState.INTERLEVEL: 'interlevel',
            GameState.GAME_OVER: 'game_over',
            GameState.VICTORY: 'interlevel',  # Misma música que interlevel
            GameState.SETTINGS: 'menu',
            GameState.HIGHSCORES: 'menu',
            GameState.INFO: 'menu'
        }

        track_name = music_map.get(self.state)
        if track_name:
            self.play_music(track_name)








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
        elif self.state == GameState.SETTINGS:
            self.settings_screen.draw(window)
        elif self.state == GameState.HIGHSCORES:
            self.high_scores_screen.draw(window)
        elif self.state == GameState.INFO:
            self.info_screen.draw(window)


        pygame.display.flip()

    def draw_menu(self):
        self.background.update()
        self.background.draw(window)
        if self.title_image:
            window.blit(self.title_image, self.title_rect)
        else:
            title = TITLE_FONT.render("BOMB'S BEFORE", True, WHITE)
            window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        self.start_button.draw(window)
        self.settings_button.draw(window)
        self.records_button.draw(window)
        self.info_button.draw(window)

    def draw_character_select(self):
        # 1. Fondo animado
        self.background.update()
        self.background.draw(window)

        # 2. Título con sombra y efecto
        title = TITLE_FONT.render("SELECCIONA TU PERSONAJE", True, WHITE)
        title_shadow = TITLE_FONT.render("SELECCIONA TU PERSONAJE", True, (50, 50, 50, 150))
        title_y = HEIGHT // 6  # Ajustado a 1/6 de la pantalla (antes 1/4)

        # Dibujar sombra y texto
        window.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, title_y + 3))
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, title_y))

        # 3. Cargar iconos (hazlo en __init__ y reutiliza)
        if not hasattr(self, 'char_icons'):
            self.char_icons = {
                0: pygame.image.load("assets/textures/bg/bomber_icon.png").convert_alpha(),
                1: pygame.image.load("assets/textures/bg/tanky_icon.png").convert_alpha(),
                2: pygame.image.load("assets/textures/bg/pyro_icon.png").convert_alpha(),
                3: pygame.image.load("assets/textures/bg/cleric_icon.png").convert_alpha()
            }

            item_icons = {
                0: None,  # Bomber
                1: "has_shield",  # Tanky
                2: "bullet_heal",  # Pyro
                3: "shotgun"  # Cleric
            }

            # Escalar si es necesario
            for k in self.char_icons:
                self.char_icons[k] = pygame.transform.scale(self.char_icons[k], (60, 60))

        # 4. Cuadrícula mejorada
        cols = 2
        button_width, button_height = 220, 80
        padding = 40
        start_x = WIDTH // 2 - (cols * (button_width + padding)) // 2
        start_y = HEIGHT // 3

        for i, button in enumerate(self.character_buttons):
            row = i // cols
            col = i % cols

            # Posición con animación de entrada
            target_x = start_x + col * (button_width + padding)
            target_y = start_y + row * (button_height + 120)

            # Animación suave
            if not hasattr(button, 'anim_x'):
                button.anim_x, button.anim_y = target_x - 100, target_y
            button.anim_x += (target_x - button.anim_x) * 0.1
            button.anim_y += (target_y - button.anim_y) * 0.1

            button.rect.x, button.rect.y = button.anim_x, button.anim_y

            # 5. Glow effect al hacer hover
            if button.is_hovered:
                glow_size = 20 * (1 + math.sin(pygame.time.get_ticks() * 0.005))
                glow_surf = pygame.Surface((button_width + glow_size, button_height + glow_size), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*button.color[:3], 30), glow_surf.get_rect(), border_radius=15)
                window.blit(glow_surf, (button.rect.x - glow_size // 2, button.rect.y - glow_size // 2))

            # 6. Dibujar botón con sombra
            pygame.draw.rect(window, (30, 30, 30), button.rect.inflate(8, 8), border_radius=12)
            button.draw(window)

            # 7. Icono del personaje (con animación)
            icon = self.char_icons[i]
            icon_y = button.rect.y - 50 + math.sin(pygame.time.get_ticks() * 0.001 + i) * 5
            window.blit(icon, (button.rect.centerx - 30, icon_y))

            # 8. Tarjeta de descripción
            card_rect = pygame.Rect(
                button.rect.x - 10,
                button.rect.bottom + 10,
                button_width + 20,
                100
            )

            # Fondo con gradiente
            card_surf = pygame.Surface((card_rect.w, card_rect.h), pygame.SRCALPHA)
            for y in range(card_rect.h):
                alpha = 150 - int(y / card_rect.h * 50)
                pygame.draw.line(card_surf, (*button.color[:3], alpha), (0, y), (card_rect.w, y))
            window.blit(card_surf, card_rect)

            # 9. Texto con iconos
            desc_lines = self.character_descriptions[i]
            for j, line in enumerate(desc_lines):
                text = DEFAULT_FONT.render(line, True, WHITE)
                window.blit(text, (button.rect.x + 10, button.rect.bottom + 10 + j * 25))

                # Dibuja el ítem al lado (derecha del botón)
            item_key = self.character_items[i]  # Usa self.
            if item_key and item_key in self.item_icons:  # Usa self.
                item_img = self.item_icons[item_key]
                window.blit(item_img, (button.rect.right + 10, button.rect.centery - 20))


    def draw_game(self):
        current_level = self.levels[self.current_level_index]

        # Dibujar mapa
        for block in current_level.map:
            if not block.destroyed:
                block.draw(window)
        # Dibujar trampas
        #for trap in current_level.traps:
            #trap.draw(window)


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



        self.player.draw(window)
        self.player.draw_items(window)
        # Dibujar HUD
        lives_text = DEFAULT_FONT.render(f"Vidas: {self.player.lives}", True, WHITE)
        score_text = DEFAULT_FONT.render(f"Puntos: {self.score}", True, WHITE)
        level_text = DEFAULT_FONT.render(
            f"Nivel: {self.current_level_index + 1}/{len(self.levels)}",
            True, WHITE)
        bombs_text = DEFAULT_FONT.render(
            f"Bombas: {self.player.available_bombs}",
            True, WHITE)

        window.blit(lives_text, (10, 10))
        window.blit(score_text, (10, 50))
        window.blit(level_text, (WIDTH - 150, 10))
        window.blit(bombs_text, (WIDTH - 150, 50))

        # Mostrar si tiene la llave
        key_text = DEFAULT_FONT.render(
            "Llave: " + ("Si" if self.player.key_collected else "X"),
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

        if self.current_music != 'game_over':
            self.play_music('game_over')

    def draw_victory(self):
        if self.score > 0:
            self.score_manager.add_score("Jugador", self.score)
        text = DEFAULT_FONT.render("¡VICTORIA!", True, GREEN)
        score = DEFAULT_FONT.render(f"Puntuación final: {self.score}", True, WHITE)

        play_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = DEFAULT_FONT.render(f"Tiempo: {play_time} segundos", True, WHITE)

        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
        window.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 20))
        window.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 40))

        restart = DEFAULT_FONT.render("Haz clic para volver al menú", True, WHITE)
        window.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 100))

        if self.current_music != 'interlevel':
            self.play_music('interlevel')



    Powerup.load_sprites()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        self.play_music("menu")
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