from datetime import datetime
import os

import pygame
from enum import Enum



def load_fonts(size=20):
    # Asegúrate de que pygame.font esté inicializado
    if not pygame.font.get_init():
        pygame.font.init()

    font_path = os.path.join("..", "assets", "fonts", "default.ttf")
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)


    # Fallback a fuentes seguras
    return pygame.font.SysFont("Arial", size)



# No cargues las fuentes aquí. Solo declara las variables.
DEFAULT_FONT = None
TITLE_FONT = None

DEFAULT_FONT = load_fonts(20)
TITLE_FONT = load_fonts(30)

MAP_WIDTH, MAP_HEIGHT = 1280, 800
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60
GREEN, RED, WHITE, YELLOW, BROWN, GRAY, BLUE, ORANGE, BLACK = ((0, 255, 0), (255, 0, 0), (255, 255, 255), (255, 215, 0),
                                                               (150, 75, 0),
                                                               (100, 100, 100), (0, 0, 255), (255, 100, 0), (0, 0, 0))


class GameState(Enum):
    MENU = 0
    CHARACTER_SELECT = 1
    GAME = 2
    INTERLEVEL = 3
    GAME_OVER = 4
    VICTORY = 5
    SETTINGS = 6
    HIGHSCORES = 7
    INFO = 8


class Difficulty(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    TRANSITION_ROOM = 3
    FINAL_BOSS = 4


class PowerupType(Enum):
    EXTRA_LIFE = 0
    EXTRA_BOMB = 1
    EXTRA_VELOCITY = 2
    EXTRA_DAMAGE = 3
    EXPLOSION_RANGE = 4
    BOMB_IMMUNITY = 5
    PHASE_TROUGH = 6
    FREEZE_ENEMIES = 7


class ScrollingBackground:
    def __init__(self, image_path, speed=1):
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        self.width = self.image.get_width()
        self.scroll = 0
        self.speed = speed

    def update(self):
        self.scroll -= self.speed
        if self.scroll < -self.width:
            self.scroll = 0

    def draw(self, surface):
        surface.blit(self.image, (self.scroll, 0))
        surface.blit(self.image, (self.scroll + self.width, 0))


class ScoreManager:
    def __init__(self, filename="highscores.txt", max_scores=10):
        # Obtiene la ruta absoluta del directorio donde está este archivo (utils.py)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Combina con el nombre del archivo para obtener la ruta completa
        self.filename = os.path.join(current_dir, filename)
        self.max_scores = max_scores
        self.scores = []
        self.load_scores()

    def load_scores(self):
        """Carga los puntajes desde el archivo, crea el archivo si no existe"""
        try:
            with open(self.filename, "r") as f:
                for line in f:
                    if line.strip():
                        name, score, date = line.strip().split(",")
                        self.scores.append((name, int(score), date))
        except FileNotFoundError:
            # Si el archivo no existe, lo crea vacío
            open(self.filename, 'w').close()
        except Exception as e:
            # Si hay otro error, inicializa con lista vacía
            self.scores = []

    def save_scores(self):
        """Guarda los puntajes en el archivo"""
        try:
            with open(self.filename, "w") as f:
                for name, score, date in self.scores[:self.max_scores]:
                    f.write(f"{name},{score},{date}\n")
        except Exception as e:
            print(f"Error al guardar puntajes: {e}")

    def add_score(self, name, score):
        """Añade un nuevo puntaje y guarda"""
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.scores.append((name, score, date))
        # Ordena de mayor a menor puntaje
        self.scores.sort(key=lambda x: x[1], reverse=True)
        # Mantiene solo los mejores puntajes
        self.scores = self.scores[:self.max_scores]
        self.save_scores()

    def get_top_scores(self, count=5):
        return self.scores[:count]

class SettingScreen:
    def __init__(self):
        self.buttons = []
        self.sliders = []
        self.checkboxes = []

        self._setup_ui()

    def _setup_ui(self):
        self.music_slider = Slider(
            x=WIDTH // 2 - 150, y=150, width=300, height=20,
            min_val=0, max_val=100, initial_val=50,
            color=GRAY, hover_color=BLUE
        )

        # Slider para volumen de efectos
        self.sfx_slider = Slider(
            x=WIDTH // 2 - 150, y=250, width=300, height=20,
            min_val=0, max_val=100, initial_val=70,
            color=GRAY, hover_color=BLUE
        )

        # Checkbox para pantalla completa
        self.fullscreen_check = Checkbox(
            x=WIDTH // 2 - 150, y=350, size=30,
            checked=False, color=GRAY, hover_color=BLUE
        )

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True

        # Verificar sliders
        self.music_slider.handle_event(event)
        self.sfx_slider.handle_event(event)

        # Verificar checkbox
        self.fullscreen_check.handle_event(event)



        # Verificar botón de volver


        return None

    def draw(self, surface):
        """Dibuja la pantalla de configuración"""
        surface.fill(BLACK)

        # Título
        title = TITLE_FONT.render("CONFIGURACIÓN", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Volumen de música
        music_label = DEFAULT_FONT.render("Volumen Música:", True, WHITE)
        surface.blit(music_label, (WIDTH // 2 - 150, 120))
        self.music_slider.draw(surface)
        music_value = DEFAULT_FONT.render(f"{int(self.music_slider.value)}%", True, WHITE)
        surface.blit(music_value, (WIDTH // 2 + 160, 145))

        # Volumen de efectos
        sfx_label = DEFAULT_FONT.render("Volumen Efectos:", True, WHITE)
        surface.blit(sfx_label, (WIDTH // 2 - 150, 220))
        self.sfx_slider.draw(surface)
        sfx_value = DEFAULT_FONT.render(f"{int(self.sfx_slider.value)}%", True, WHITE)
        surface.blit(sfx_value, (WIDTH // 2 + 160, 245))

        # Pantalla completa
        fullscreen_label = DEFAULT_FONT.render("Pantalla Completa:", True, WHITE)
        surface.blit(fullscreen_label, (WIDTH // 2 - 150, 320))
        self.fullscreen_check.draw(surface)


        # Botón de volver

class HighScoresScreen:
    """Pantalla de mejores puntajes"""
    def __init__(self, score_manager):
        self.score_manager = score_manager


    def handle_event(self, event):
        """Maneja eventos de la pantalla de puntajes"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True


        return None

    def draw(self, surface):
        surface.fill(BLACK)

        # Título centrado
        title = TITLE_FONT.render("MEJORES PUNTAJES", True, YELLOW)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # Encabezados de columnas
        headers = ["POS", "JUGADOR", "PUNTAJE", "FECHA"]
        header_x_positions = [80, 240, 400, 560]  # Posiciones X ajustadas

        for i, header in enumerate(headers):
            text = DEFAULT_FONT.render(header, True, WHITE)
            surface.blit(text, (header_x_positions[i] - text.get_width() // 2, 100))

        # Línea divisoria
        pygame.draw.line(surface, WHITE, (50, 130), (WIDTH - 50, 130), 2)

        # Puntajes
        scores = self.score_manager.get_top_scores(10)
        for i, (name, score, date) in enumerate(scores):
            y_pos = 150 + i * 40

            # Posición
            pos_text = DEFAULT_FONT.render(f"{i + 1}.", True, WHITE)
            surface.blit(pos_text, (header_x_positions[0] - pos_text.get_width() // 2, y_pos))

            # Nombre (limitado a 12 caracteres)
            name_text = DEFAULT_FONT.render(name[:12], True, WHITE)
            surface.blit(name_text, (header_x_positions[1] - name_text.get_width() // 2, y_pos))

            # Puntaje
            score_text = DEFAULT_FONT.render(str(score), True, WHITE)
            surface.blit(score_text, (header_x_positions[2] - score_text.get_width() // 2, y_pos))

            # Fecha (solo día/mes)
            short_date = "/".join(date.split()[0].split("-")[1:3])
            date_text = DEFAULT_FONT.render(short_date, True, WHITE)
            surface.blit(date_text, (header_x_positions[3] - date_text.get_width() // 2, y_pos))

        # Botón de volver



class ScrollableInfoScreen:
    def __init__(self):
        self.scroll_y = 0
        self.scroll_speed = 30

        self.scroll_area = pygame.Rect(0, 0, WIDTH, HEIGHT - 100)
        self.content_height = 1200
        self.dev_image = pygame.image.load("assets/textures/bg/dev_photo.jpg").convert_alpha()
        self.dev_image = pygame.transform.scale(self.dev_image, (150, 150))
        self.lines = self._prepare_text()

        # Bandera para controlar el enfoque del scroll
        self.scroll_focused = False

    def _prepare_text(self):
        info_text = [
            "DESARROLLADOR:",
            "Nombre: Juan José Rodríguez Chaves",
            "Carné: 2025094370",
            "Institución: Tecnológico de Costa Rica (TEC)",
            "Carrera: Ingeniería en Computadores",
            "Curso: Introducción a la Programación",
            "Profesores: Diego Mora Rojas y Jeff Schmidt Peralta",
            "Año: 2025",
            "País: Costa Rica",
            "Versión: 1.0",
            "",
            "ACERCA DEL JUEGO:",
            "Bomb's Before es un juego de acción y estrategia",
            "donde debes colocar bombas para eliminar enemigos",
            "y encontrar la llave para avanzar.",
            "",
            "CONTROLES:",
            "- WASD: Movimiento",
            "- E: Colocar bomba",
            "- Flechas: Disparar",
            "- Espacio: Usar power-up",
            "- ESC: Menú principal"
        ]
        return info_text

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

        # Manejar scroll con rueda del ratón
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self.content_height - self.scroll_area.height))

        # Verificar si el ratón está sobre el área desplazable
        if event.type == pygame.MOUSEMOTION:
            self.scroll_focused = self.scroll_area.collidepoint(event.pos)

        # Manejar arrastre para scroll (opcional)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scroll_focused:
                self.drag_start_y = mouse_pos[1]
                self.drag_start_scroll = self.scroll_y

        if event.type == pygame.MOUSEMOTION and event.buttons[0] and hasattr(self, 'drag_start_y'):
            delta_y = mouse_pos[1] - self.drag_start_y
            self.scroll_y = self.drag_start_scroll - delta_y
            self.scroll_y = max(0, min(self.scroll_y, self.content_height - self.scroll_area.height))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if hasattr(self, 'drag_start_y'):
                delattr(self, 'drag_start_y')

        # Botón de volver


        return None

    def draw(self, surface):
        # Fondo
        surface.fill(BLACK)

        # Crear superficie para el contenido desplazable
        content_surface = pygame.Surface((WIDTH, self.content_height))
        content_surface.fill(BLACK)

        # Dibujar contenido
        y_offset = 20 - self.scroll_y

        # Imagen del desarrollador
        if y_offset + 150 > 0 and y_offset < HEIGHT:
            content_surface.blit(self.dev_image, (WIDTH // 2 - 75, y_offset))
        y_offset += 180

        # Texto
        for line in self.lines:
            if y_offset + 30 > 0 and y_offset < HEIGHT:
                color = YELLOW if line.endswith(":") else WHITE
                font = DEFAULT_FONT if not line.endswith(":") else TITLE_FONT
                text = font.render(line, True, color)
                content_surface.blit(text, (50, y_offset))
            y_offset += 40

        # Dibujar área visible
        surface.blit(content_surface, (0, 0), self.scroll_area)

        # Barra de scroll
        if self.content_height > self.scroll_area.height:
            scroll_ratio = self.scroll_area.height / self.content_height
            scrollbar_height = max(30, self.scroll_area.height * scroll_ratio)
            scroll_pos = (self.scroll_y / self.content_height) * self.scroll_area.height

            pygame.draw.rect(surface, GRAY, (WIDTH - 10, scroll_pos, 8, scrollbar_height))

        # Botón de volver (siempre visible)



class Slider:
    """Control deslizante para ajustar valores"""

    def __init__(self, x, y, width, height, min_val, max_val, initial_val, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(x, y - 5, 20, height + 10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.color = color
        self.hover_color = hover_color
        self.dragging = False
        self._update_knob_pos()

    def _update_knob_pos(self):
        """Actualiza la posición del knob basado en el valor actual"""
        value_range = self.max_val - self.min_val
        knob_pos = ((self.value - self.min_val) / value_range) * self.rect.width
        self.knob_rect.x = self.rect.x + knob_pos - self.knob_rect.width // 2

    def handle_event(self, event):
        """Maneja eventos del slider"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
            elif self.rect.collidepoint(event.pos):
                # Hacer clic en la barra para mover el knob
                rel_x = event.pos[0] - self.rect.x
                self.value = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
                self._update_knob_pos()

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = event.pos[0] - self.rect.x
            rel_x = max(0, min(self.rect.width, rel_x))
            self.value = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self._update_knob_pos()

    def draw(self, surface):
        """Dibuja el slider"""
        # Barra del slider
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)

        # Knob del slider
        knob_color = self.hover_color if self.dragging else self.color
        pygame.draw.rect(surface, knob_color, self.knob_rect, border_radius=5)

class Checkbox:
    """Checkbox para opciones binarias"""

    def __init__(self, x, y, size, checked, color, hover_color):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = checked
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def handle_event(self, event):
        """Maneja eventos del checkbox"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False

    def draw(self, surface):
        """Dibuja el checkbox"""
        # Marco exterior
        pygame.draw.rect(surface, self.hover_color if self.is_hovered else self.color, self.rect, 2)

        # Marca de verificación si está seleccionado
        if self.checked:
            pygame.draw.rect(surface, self.hover_color if self.is_hovered else self.color,
                             self.rect.inflate(-8, -8))