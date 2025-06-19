import sys
import pygame
import random

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


#EN PROCESO
Mejora de una estadistica al terminar un nivel
#Los enemigos hacen el doble de danio pero tu daño incrementa en +5 - XV The Devil
# x1.5 De velocidad por todo el juego - O The Fool
#El siguiente hit no te hace dano - VII The Chariot
# Por todo el juego tienes una probabilidad de revivir de un 25% con 1 de vida - XIX The Sun
#Tus ataque persiguen a los enemigos - I The Magician
#Escopeta - II The High Priestess
#Cada 20 ataques que inflingan daño te curas 1 corazón - VI The Lovers 
class Items:


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


        try:
            self.title_image = pygame.image.load("assets/textures/bg/title2.png").convert_alpha()
            self.title_image = pygame.transform.smoothscale(self.title_image, (408, 612))  # Ajusta el tamaño
            self.title_rect = self.title_image.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        except:
            self.title_image = None

        self.frozen_enemies = False  # Para control global

    def start_game(self, character_type):
        self.levels = [
            Level(1, Difficulty.EASY, self),
            Level(2, Difficulty.MEDIUM, self),
            Level(3, Difficulty.HARD, self),
            Level(4, Difficulty.FINAL_BOSS, self)]
        self.current_level_index = 0

        # Crear jugador según el tipo seleccionado
        if character_type == 0:  # Bomber
            self.player = Player(1, 1, 3, 3, BLUE, 51, 0, self)
        elif character_type == 1:  # Tanky
            self.player = Player(1, 1, 5, 2, GREEN, 3, 1, self)
        elif character_type == 2:  # Pyro
            self.player = Player(1, 1, 2, 5, RED, 8, 2, self)
        elif character_type == 3: #Cleric
            self.player = Player(1, 1, 2, 4, WHITE, 4, 3, self)

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

    def next_level(self):
        self.state = GameState.INTERLEVEL
        self.interlevel_screen = InterLevelScreen(self.player)
        if self.current_level_index >= len(self.levels) - 1:
            self.state = GameState.VICTORY
            return False

        self.current_level_index += 1

        current_level = self.levels[self.current_level_index]
        current_level.__init__(current_level.number, current_level.difficulty, self)

            # Reposicionar al jugador
        self.player.rect.x = TILE_SIZE
        self.player.rect.y = TILE_SIZE
        self.player.hitbox.x = self.player.rect.x + 5
        self.player.hitbox.y = self.player.rect.y + 5

        self.player.key_collected = False
        self.player.invincible = False
        self.player.visible = True

        self.ensure_starting_position()

        self.player.active_effects = {
            "bomb_immune": False,
            "phase_through": False
        }
        self.frozen_enemies = False

        # Resetear arma
        self.player.weapon.damage = self.player.weapon.base_damage
        self.player.weapon.speed = 10  # Velocidad base
        return True

    def handle_interlevel_events(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.spinning_roulette = True  # Iniciar animación

        if self.spinning_roulette:
            self.animate_roulette()
        else:

            choice = self.interlevel_screen.get_choice(mouse_pos, mouse_click)
            if choice == 4:
                self.spinning_roulette = True
            elif choice is not None:
                self.apply_choice(choice)

    def apply_choice(self, choice):
        if choice == 0:
            self.player.bomb_capacity += 2
        if choice == 1:
            self.player.health += 2
        if choice == 2:
            self.player.speed += 2
        if choice == 3:
            self.player.damage += 2
        if choice == 4:
            item = random.choice(self.interlevel_screen.items)
            self.apply_item_effect(item["effect"])


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
                print("Enemigos descongelados")

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

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

        for enemy in current_level.enemies:
            enemy.update(current_level.map)

        self.player.update_weapon(current_level)

        for bullet in self.player.weapon.bullets[:]:
            for enemy in current_level.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.take_damage(bullet.damage)
                    self.player.weapon.bullets.remove(bullet)
                    if enemy.state == "dead":
                        current_level.enemies.remove(enemy)
                    break



        for bomb in self.player.bombs[:]:
            if bomb.update(current_level):
                current_level.check_bomb_collisions(bomb, self.player)
                self.player.bombs.remove(bomb)



        for enemy in current_level.enemies:
            if (enemy.state != "dead" and
                    self.player.hitbox.colliderect(enemy.rect) and
                    not self.player.invincible):

                self.player.take_damage()
                if self.player.take_damage():
                    self.player.update_invincibility()

            if self.player.lives <= 0:
                self.state = GameState.GAME_OVER
                return

        current_level = self.levels[self.current_level_index]

        if (hasattr(current_level, 'key') and
                current_level.key.revealed and
                not current_level.key.collected and
                self.player.hitbox.colliderect(current_level.key.rect)):

                current_level.key.collected = True
                self.player.key_collected = True
                current_level.open_door()

        if current_level.door.open and self.player.hitbox.colliderect(current_level.door.rect):
            self.next_level()
            self.score += 500





    def draw(self):
        window.fill(BLACK)

        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.CHARACTER_SELECT:
            self.draw_character_select()
        elif self.state == GameState.GAME:
            self.draw_game()
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