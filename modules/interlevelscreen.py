import pygame
import random
from modules.utils import WHITE, BLACK, WIDTH, DEFAULT_FONT, TITLE_FONT, GREEN
from modules.button import Button


class InterLevelScreen:
    def __init__(self, player):
        self.player = player
        self.buttons = [
            Button(100, 200, 200, 50, "+1 Bomba", WHITE, BLACK, font=DEFAULT_FONT),
            Button(100, 300, 200, 50, "+1 Vida", WHITE, BLACK, font=DEFAULT_FONT),
            Button(100, 400, 200, 50, "+1 Velocidad", WHITE, BLACK, font=DEFAULT_FONT),
            Button(100, 500, 200, 50, "+1 Daño", WHITE, BLACK, font=DEFAULT_FONT),
            Button(400, 350, 200, 50, "Ruleta de Items", (255, 215, 0), BLACK, font=DEFAULT_FONT),
            Button(400, 450, 200, 50, "Omitir", (200, 200, 200), BLACK, font=DEFAULT_FONT)]

        self.items = [
            {"name": "O The Fool", "effect": "speed_boost", "desc": "Velocidad x1.5 permanente"},
            {"name": "I The Magician", "effect": "homing_bullets", "desc": "Balas persiguen enemigos"},
            {"name": "II The High Priestess", "effect": "shotgun", "desc": "Disparo en abanico"},
            {"name": "VI The Lovers", "effect": "bullet_heal", "desc": "+1 vida cada 20 golpes"},
            {"name": "VII The Chariot", "effect": "one_shield", "desc": "Escudo contra 1 golpe"},
            {"name": "XV The Devil", "effect": "double_damage", "desc": "+5 daño (enemigos x2 daño)"},
            {"name": "XIX The Sun", "effect": "revive_chance", "desc": "25% de revivir al morir"},
            {"name": "XVI The Tower", "effect": "indestructible_bomb", "desc": "Bombas rompen bloques indestructibles"}]

        self.item_images = {"O The Fool": pygame.image.load("assets/textures/items/the_fool.png").convert_alpha(),
                            "I The Magician": pygame.image.load("assets/textures/items/the_magician.png").convert_alpha(),
                            "II The High Priestess": pygame.image.load("assets/textures/items/the_high_priestess.png").convert_alpha(),
                            "VI The Lovers": pygame.image.load("assets/textures/items/the_lovers.png").convert_alpha(),
                            "VII The Chariot": pygame.image.load("assets/textures/items/the_chariot.png").convert_alpha(),
                            "XV The Devil": pygame.image.load("assets/textures/items/the_chariot.png").convert_alpha(),
                            "XIX The Sun": pygame.image.load("assets/textures/items/the_sun.png").convert_alpha(),
                            "XVI The Tower": pygame.image.load("assets/textures/items/the_tower.png").convert_alpha()}

        self.selected_item = None
        self.showing_item = False
        self.item_confirmed = False

        for item in self.item_images:
            self.item_images[item] = pygame.transform.scale(self.item_images[item], (64, 64))


    def draw(self, surface):
        surface.fill(BLACK)
        title = TITLE_FONT.render("Elige una mejora:", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        if not self.showing_item:
            for btn in self.buttons:
                btn.draw(surface)
        else:
            # Mostrar el item seleccionado
            item = self.selected_item
            item_name = TITLE_FONT.render(item["name"], True, (255, 215, 0))
            item_desc = DEFAULT_FONT.render(item["desc"], True, WHITE)

            surface.blit(item_name, (WIDTH // 2 - item_name.get_width() // 2, 200))
            surface.blit(item_desc, (WIDTH // 2 - item_desc.get_width() // 2, 250))

            confirm_btn = Button(WIDTH // 2 - 100, 350, 200, 50, "Confirmar", GREEN, BLACK, font=DEFAULT_FONT)
            confirm_btn.draw(surface)

            if confirm_btn.is_clicked(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
                self.item_confirmed = True

    def get_choice(self, mouse_pos, click):
        if self.showing_item and not self.item_confirmed:
            return None

        for i, btn in enumerate(self.buttons):
            if btn.is_clicked(mouse_pos, click):
                if i == 4:
                    self.selected_item =random.choice(self.items)
                    self.showing_item = True
                    return None
                elif i == 5:
                    return "omitir"
                else:
                    return i
        return None

