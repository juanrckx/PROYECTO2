import sys
import pygame

from modules.button import Button
from modules.level import Level
from modules.player import Player
from modules.utils import GameState, Difficulty, GREEN, RED, BLUE, BLACK, HEIGHT, WIDTH, TILE_SIZE, FPS, WHITE
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

Bloques destructibles e indestructibles YA
Llave Oculta en un bloque destructible YA
Mejora de una estadistica al terminar un nivel
Dificultad 

Items y Powerups
#Aumento +1 de vida
#Aumento rango de explosion
#Bombas no hacen danio al jugador
#Puedes atravesar bloques por 5 segundos
#Los enemigos se detienen por 7 segundos
#Aumento +1 bombas
class Powerups:


#Los enemigos hacen el doble de danio pero el mapa tiene menos obstaculos
# x1.5 De velocidad por todo el juego
#El siguiente hit no te hace dano
# Por todo el juego tienes una probabilidad de revivir de un 25% con 1 de vida
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
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomb's Before")
clock = pygame.time.Clock()
info = pygame.display.Info()

real_width, real_height = info.current_w, info.current_h
v_screen = pygame.Surface((800, 600))
screen = pygame.display.set_mode((real_width, real_height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
fullscreen = True


class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.levels = [
            Level(1, Difficulty.EASY),
            Level(2, Difficulty.MEDIUM),
            Level(3, Difficulty.HARD),
            Level(4, Difficulty.FINAL_BOSS)
        ]
        self.current_level_index = 0
        self.player = None
        self.score = 0
        self.start_time = 0
        self.font = pygame.font.SysFont("Arial", 30)

        # Botones del menú
        self.start_button = Button(
            WIDTH // 2 - 100, HEIGHT // 2, 200, 50,
            "COMENZAR", GREEN, (100, 255, 100))

        # Botones de selección de personaje
        self.character_buttons = [
            Button(
                WIDTH // 4 - 75, HEIGHT // 2 + 100, 150, 50,
                "BOMBER", BLUE, (100, 100, 255)),
            Button(
                WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 50,
                "TANKY", GREEN, (100, 255, 100)),
            Button(
                3 * WIDTH // 4 - 75, HEIGHT // 2 + 100, 150, 50,
                "PYRO", (255, 0, 0), (255, 100, 100))
        ]

        # Textos descriptivos de personajes
        self.character_descriptions = [
            ["Vida: 3", "Velocidad: 3", "Bombas: 3"],
            ["Vida: 5", "Velocidad: 2", "Bombas: 2"],
            ["Vida: 2", "Velocidad: 4", "Bombas: 4"]
        ]

    def start_game(self, character_type):
        self.levels = [
            Level(1, Difficulty.EASY),
            Level(2, Difficulty.MEDIUM),
            Level(3, Difficulty.HARD),
            Level(4, Difficulty.FINAL_BOSS)]
        self.current_level_index = 0

        # Crear jugador según el tipo seleccionado
        if character_type == 0:  # Bomber
            self.player = Player(1, 1, 3, 3, BLUE, 3)
        elif character_type == 1:  # Tanky
            self.player = Player(1, 1, 5, 2, GREEN, 2)
        elif character_type == 2:  # Pyro
            self.player = Player(1, 1, 2, 5, RED, 4)
        elif character_type == 3:
            self.player = Player(1, 1, 2, 4, WHITE, 2)

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
        if self.current_level_index >= len(self.levels) - 1:
            self.state = GameState.VICTORY
            return False

        self.current_level_index += 1

        current_level = self.levels[self.current_level_index]
        current_level.__init__(current_level.number, current_level.difficulty)

            # Reposicionar al jugador y resetear bombas
        self.player.rect.x = TILE_SIZE
        self.player.rect.y = TILE_SIZE
        self.player.hitbox.x = self.player.rect.x + 5
        self.player.hitbox.y = self.player.rect.y + 5

        self.player.key_collected = False
        self.player.invincible = False
        self.player.visible = True

        self.ensure_starting_position()
        return True

    def handle_events(self):
        global fullscreen, screen, real_width, real_height, v_screen
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

            if event.type == pygame.KEYDOWN:
                if self.state == GameState.GAME and event.key == pygame.K_e:
                    self.player.player_place_bomb()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(
                            (real_width, real_height),
                            pygame.FULLSCREEN)
        scaled_screen = pygame.transform.scale(v_screen, (real_width, real_height))
        screen.blit(scaled_screen, (0, 0))
        pygame.display.flip()



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
        keys = pygame.key.get_pressed()

        # Movimiento del jugador
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        self.player.move(dx, dy, current_level.map)

        for enemy in current_level.enemies:
            enemy.update(current_level.map)

        # Actualizar bombas
        for bomb in self.player.bombs[:]:
            if bomb.update():
                current_level.check_bomb_collisions(bomb, self.player)
                self.player.bombs.remove(bomb)


        # Actualizar enemigos
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

            # Verificar colisión con explosiones
        for bomb in self.player.bombs[:]:
            if bomb.exploded:
                for exp_rect in bomb.explosion_rects:
                    if (self.player.hitbox.colliderect(exp_rect) and
                            not self.player.invincible):
                        self.player.take_damage()
                        if self.player.take_damage():
                            self.player.update_invincibility()
                        break

        current_level = self.levels[self.current_level_index]
        if current_level.key and not current_level.key.collected:
            if any(block.revealed_key for block in current_level.map if hasattr(block, 'has_key') and block.has_key):
                current_level.key.draw(window)
                current_level.key_collected = True
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
        title = self.font.render("BOMB'S BEFORE", True, WHITE)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        self.start_button.draw(window)

    def draw_character_select(self):
        title = self.font.render("SELECCIONA TU PERSONAJE", True, WHITE)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        # Dibujar botones de personajes
        for button in self.character_buttons:
            button.draw(window)

        # Dibujar descripciones de personajes sin superposición
        desc_font = pygame.font.SysFont("Arial", 20)
        for i, desc_lines in enumerate(self.character_descriptions):
            x_pos = self.character_buttons[i].rect.x
            y_pos = self.character_buttons[i].rect.y - 10 - len(desc_lines) * 25

            for j, line in enumerate(desc_lines):
                text = desc_font.render(line, True, WHITE)
                window.blit(text, (x_pos, y_pos + j * 25))

    def draw_game(self):
        current_level = self.levels[self.current_level_index]

        # Dibujar mapa
        for block in current_level.map:
            block.draw(window)

        # Dibujar puerta y llave
        current_level.door.draw(window)
        if current_level.key and not current_level.key.collected:
            current_level.key.draw(window)

        # Dibujar enemigos
        for enemy in current_level.enemies:
            enemy.draw(window)

        # Dibujar bombas
        for bomb in self.player.bombs:
            bomb.draw(window)

        # Dibujar jugador
        self.player.draw(window)

        # Dibujar HUD
        lives_text = self.font.render(f"Vidas: {self.player.lives}", True, WHITE)
        score_text = self.font.render(f"Puntos: {self.score}", True, WHITE)
        level_text = self.font.render(
            f"Nivel: {self.current_level_index + 1}/{len(self.levels)}",
            True, WHITE)
        bombs_text = self.font.render(
            f"Bombas: {self.player.available_bombs}/{self.player.bomb_capacity}",
            True, WHITE)

        window.blit(lives_text, (10, 10))
        window.blit(score_text, (10, 50))
        window.blit(level_text, (WIDTH - 150, 10))
        window.blit(bombs_text, (WIDTH - 150, 50))

        # Mostrar si tiene la llave
        key_text = self.font.render(
            "Llave: " + ("Sí" if self.player.key_collected else "No"),
            True, WHITE)
        window.blit(key_text, (WIDTH // 2 - key_text.get_width() // 2, 10))


    def draw_game_over(self):
        text = self.font.render("GAME OVER", True, RED)
        score = self.font.render(f"Puntuación final: {self.score}", True, WHITE)
        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))
        window.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 + 20))

        restart = self.font.render("Haz clic para volver al menú", True, WHITE)
        window.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 80))

    def draw_victory(self):
        text = self.font.render("¡VICTORIA!", True, GREEN)
        score = self.font.render(f"Puntuación final: {self.score}", True, WHITE)

        play_time = (pygame.time.get_ticks() - self.start_time) // 1000
        time_text = self.font.render(f"Tiempo: {play_time} segundos", True, WHITE)

        window.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
        window.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 20))
        window.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2 + 40))

        restart = self.font.render("Haz clic para volver al menú", True, WHITE)
        window.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 100))

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
            if self.state == GameState.GAME:
                self.player.update_invincibility()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()