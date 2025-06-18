import pygame
import random
from modules.utils import WHITE, BLACK, WIDTH, DEFAULT_FONT, TITLE_FONT
from modules.button import Button


class InterLevelScreen:
    def __init__(self, player):
        self.player = player
        self.buttons = [
            Button(100, 200, 200, 50, "+1 Bomba", WHITE, BLACK, font=DEFAULT_FONT),
            Button(100, 300, 200, 50, "+1 Vida", WHITE, BLACK, font=DEFAULT_FONT),
            Button(100, 400, 200, 50, "+1 Velocidad", WHITE, BLACK, font=DEFAULT_FONT),
            Button(100, 500, 200, 50, "+1 Daño", WHITE, BLACK, font=DEFAULT_FONT),
            Button(400, 350, 200, 50, "Ruleta de Items", (255, 215, 0), BLACK, font=DEFAULT_FONT)
        ]
        self.items = [
            {"name": "O The Fool", "effect": "speed_+5"},
            {"name": "I The Magician", "effect": "bullet_trace"},
            {"name": "II The High Priestess", "effect": "shotgun"},
            {"name": "VI The Lovers", "effect": "bullet_heal"},
            {"name": "VII The Chariot", "effect": "1life_shield"},
            {"name": "XV The Devil", "effect": "double_damage"},
            {"name": "XIX The Sun", "effect": "revive"}

        ]

    def draw(self, surface):
        surface.fill(BLACK)
        title = TITLE_FONT.render("Elige una mejora:", True, WHITE)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for btn in self.buttons:
            btn.draw(surface)

    def get_choice(self, mouse_pos, click):
        for i, btn in enumerate(self.buttons):
            if btn.is_clicked(mouse_pos, click):
                return i  # 0-3: Mejoras, 4: Ruleta
        return None

    def spin_roulette(self):
        # Animación de ruleta
        selected = random.randint(0, len(self.items) - 1)
        return self.items[selected]