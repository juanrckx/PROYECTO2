import pygame
from modules.utils import WHITE


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font if font else pygame.font.Font(None, 30)  # Usa la fuente pasada o una por defecto
        self.is_hovered = False

    def draw(self, surface):
        #color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, (60, 51, 51), self.rect, 2, border_radius=10)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click
