import pygame
from pygame.locals import *

GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 700

class JumpBar(pygame.sprite.Sprite):
    jump_progress: float = 0.0

    def __init__(self):
        super().__init__()
        jump_progress = 0.0

    def update(self, j_progress):
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_SPACE]:
            j_progress += 0.02
            if j_progress >= 1:
                j_progress = 0
        return j_progress

    def draw(self, surface):
        border = pygame.draw.rect(surface, BLACK, (5, 5, 40, 140), 2)
        border = pygame.draw.rect(surface, GRAY, (7, 7, 36, 136), 0)
        scale = pygame.draw.rect(surface, GREEN, (7, 143 - (self.jump_progress * 138), 36, 138 * self.jump_progress), 20)
