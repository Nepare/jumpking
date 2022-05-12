import pygame
from pygame.locals import *

class Menu(pygame.sprite.Sprite):
    chosen: int = 0
    in_game: bool = False
    title_float = 0
    title_moving_up = 1

    def __init__(self):
        texture = pygame.image.load("textures\\menu\\menu_continue.png")
        self.rect = texture.get_rect()
        self.rect.bottomleft = (0, 700)
        self.image = texture

    def float_title(self):
        if self.title_float < 25 and self.title_float > -1:
            self.title_float += self.title_moving_up / 5
        else:
            self.title_moving_up *= -1
            self.title_float += self.title_moving_up / 5

    def update(self):
        if self.chosen == 0:
            texture = pygame.image.load("textures\\menu\\menu_continue.png")
            self.image = texture
        if self.chosen == 1:
            texture = pygame.image.load("textures\\menu\\menu_newgame.png")
            self.image = texture
        if self.chosen == 2:
            texture = pygame.image.load("textures\\menu\\menu_quit.png")
            self.image = texture

    def up(self):
        if self.chosen > 0:
            self.chosen -= 1
        else:
            self.chosen = 2

    def down(self):
        if self.chosen < 2:
            self.chosen += 1
        else:
            self.chosen = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        texture_title = pygame.image.load("textures\\menu\\menu_title.png")
        texture_title = pygame.transform.scale(texture_title, (500, 142))
        title_rect = texture_title.get_rect()
        self.float_title()
        title_rect.center = (300, 200 + self.title_float)
        surface.blit(texture_title, title_rect)
