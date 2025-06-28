import pygame


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font if font else pygame.font.Font(None, 30)  # Usa la fuente pasada o una por defecto
        self.is_hovered = False
        self.border_radius = 10

    def check_hover(self, mouse_pos):
        """Actualiza el estado hovered"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def draw(self, surface):
        """Dibuja el botón con efectos visuales"""
        # Color basado en hover
        bg_color = self.hover_color if self.is_hovered else self.color

        # Dibujar botón
        pygame.draw.rect(
            surface, bg_color, self.rect,
            border_radius=self.border_radius
        )

        # Texto centrado
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click
