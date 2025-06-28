import pygame
import random
import os
from utils import WHITE, BLACK, WIDTH, DEFAULT_FONT, TITLE_FONT, GREEN
from button import Button


class InterLevelScreen:
    def __init__(self, player):
        self.player = player
        self.buttons = self._create_buttons()
        self.items = self._load_items()
        self.selected_item = None
        self.showing_item = False
        self.item_confirmed = False
        self.choice_made = False
        self.choice = None

    def _create_buttons(self):
        """Crea y posiciona los botones correctamente"""
        return [
            Button(100, 200, 200, 50, "+2 Bomba", BLACK, BLACK, font=DEFAULT_FONT),
            Button(100, 300, 200, 50, "+2 Vida", BLACK, BLACK, font=DEFAULT_FONT),
            Button(100, 400, 200, 50, "+2 Velocidad", BLACK, BLACK, font=DEFAULT_FONT),
            Button(100, 500, 200, 50, "+2 Daño", BLACK, BLACK, font=DEFAULT_FONT),
            Button(400, 350, 200, 50, "Ruleta de Items", (255, 215, 0), BLACK, font=DEFAULT_FONT),
            Button(400, 450, 200, 50, "Omitir", (200, 200, 200), BLACK, font=DEFAULT_FONT)
        ]

    def _load_items(self):
        """Carga los items con sus imágenes"""
        items = [
            {"name": "O The Fool", "effect": "speed_boost", "desc": "¡Obtienes +5 de velocidad permanente!",
             "image": "the_fool.png"},
            {"name": "I The Magician", "effect": "homing_bullets", "desc": "Tus balas persiguen a los enemigos",
             "image": "the_magician.png"},
            {"name": "II The High Priestess", "effect": "shotgun", "desc": "Tu arma ahora es una escopeta",
             "image": "the_high_priestess.png"},
            {"name": "VI The Lovers", "effect": "bullet_heal", "desc": "Te curas cada 20 disparos",
             "image": "the_lovers.png"},
            {"name": "VII The Chariot", "effect": "has_shield", "desc": "Anulas una vez por nivel 1 punto de daño",
             "image": "the_chariot.png"},
            {"name": "XV The Devil", "effect": "double_damage", "desc": "Obtienes +5 de daño permanente, pero ahora los enemigos hacen el doble de daño",
             "image": "the_devil.png"},
            {"name": "XIX The Sun", "effect": "revive_chance", "desc": "Obtienes un 25% de probabilidad de revivir al comienzo de cada nivel",
             "image": "the_sun.png"},
            {"name": "XVI The Tower", "effect": "indestructible_bomb",
             "desc": "Tus bombas ahora rompen bloques indestructibles", "image": "the_tower.png"}]

        for item in items:
            img_path = os.path.join("assets", "textures", "items", item["image"])
            item["image_surface"] = pygame.image.load(img_path).convert_alpha()
            item["image_surface"] = pygame.transform.scale(item["image_surface"], (128, 128))


        return items

    def get_choice(self, mouse_pos, mouse_click):
        """Devuelve la elección del jugador o None si no hay selección"""
        if not mouse_click:
            return None

        if self.showing_item:
            # Botón de confirmación de ítem
            confirm_rect = pygame.Rect(WIDTH // 2 - 100, 450, 200, 50)
            if confirm_rect.collidepoint(mouse_pos):
                return {"type": "item", "effect": self.selected_item["effect"]}
            return None

        # Verificar botones de mejora
        for i, button in enumerate(self.buttons[:4]):  # Solo los 4 primeros botones
            if button.rect.collidepoint(mouse_pos):
                return {"type": "stat", "value": i}  # 0=bomba, 1=vida, etc.

        # Botón de ruleta
        if self.buttons[4].rect.collidepoint(mouse_pos):  # Ruleta
            self.selected_item = random.choice(self.items)
            self.showing_item = True
            return None

        # Botón omitir
        if self.buttons[5].rect.collidepoint(mouse_pos):  # Omitir
            return {"type": "skip"}

        return None

    def draw(self, surface):
        surface.fill(BLACK)
        title = TITLE_FONT.render("Elige una mejora:", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        if not self.showing_item:
            for btn in self.buttons:
                btn.draw(surface)
        else:
            self._draw_item_selection(surface)

    def _draw_item_selection(self, surface):
        """Dibuja la selección de ítem con confirmación"""
        item = self.selected_item
        surface.blit(item["image_surface"], (WIDTH // 2 - 64, 150))

        text_name = TITLE_FONT.render(item["name"], True, (255, 215, 0))
        text_desc = DEFAULT_FONT.render(item["desc"], True, WHITE)
        surface.blit(text_name, (WIDTH // 2 - text_name.get_width() // 2, 300))
        surface.blit(text_desc, (WIDTH // 2 - text_desc.get_width() // 2, 350))

        confirm_btn = Button(WIDTH // 2 - 100, 450, 200, 50, "Confirmar", GREEN, BLACK, font=DEFAULT_FONT)
        confirm_btn.draw(surface)

    def _create_fallback_surface(self, name):
        """Crea un ícono de reserva"""
        surface = pygame.Surface((128, 128), pygame.SRCALPHA)
        pygame.draw.rect(surface, (70, 70, 70, 200), (0, 0, 128, 128), border_radius=10)
        text = DEFAULT_FONT.render(name.split()[0], True, WHITE)
        surface.blit(text, (64 - text.get_width() // 2, 64 - text.get_height() // 2))
        return surface