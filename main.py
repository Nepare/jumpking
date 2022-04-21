import sys
import time
import math

import pygame
from pygame.locals import *

pygame.init()

FPS = pygame.time.Clock()
FPS.tick(60)

BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 800

DISPLAYSURF = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Jump King на минималках")

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

    def draw(self, surface, j_progress):
        border = pygame.draw.rect(DISPLAYSURF, BLACK, (20, 20, 40, 140), 2)
        scale = pygame.draw.rect(surface, GREEN, (22, 158 - (j_progress * 136), 36, 136 * j_progress), 20)




class Player(pygame.sprite.Sprite):
    jump_progress: float = 0.0
    falling: bool = False
    jumping: bool = False
    orient_left: bool = False
    horizontal_velocity: int = 0

    def __init__(self):
        super().__init__()
        texture_idle = pygame.image.load("textures\\king_idle.png")

        self.image = texture_idle
        self.image = pygame.transform.smoothscale(self.image,(50,50))
        self.rect = self.image.get_rect()
        self.rect.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - (self.image.get_height() / 2))

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if not self.jumping and not self.falling:
            if pressed_keys[K_SPACE]:

                if pressed_keys[K_RIGHT]:
                    self.horizontal_velocity = 1
                elif pressed_keys[K_LEFT]:
                    self.horizontal_velocity = -1
                else:
                    self.horizontal_velocity = 0

                self.jump_progress += 0.02
                J1.jump_progress = J1.update(J1.jump_progress)
                if self.jump_progress >= 1:
                    self.jump()
            else:
                if self.jump_progress > 0.0:
                    self.jump()
                    J1.jump_progress = J1.update(0)
                else:
                    if pressed_keys[K_LEFT]:
                        self.turn_left()
                        if not self.rect.center[0] - (self.rect.width / 2) <= 0:
                            self.rect.move_ip(-2,0)
                    if pressed_keys[K_RIGHT]:
                        self.turn_right()
                        if not self.rect.center[0] + (self.rect.width / 2) >= DISPLAY_WIDTH:
                            self.rect.move_ip(2,0)


        if self.jumping:
            if self.jump_progress > 0.0:
                self.rect.move_ip(0, -12 * math.sqrt(self.jump_progress))
                self.jump_progress -= 0.03

                if self.horizontal_velocity == 1:
                    self.rect.move_ip(4, 0)
                if self.horizontal_velocity == -1:
                    self.rect.move_ip(-4, 0)

                if self.rect.center[0] + (self.rect.width / 2) >= DISPLAY_WIDTH: # столкновение с правым краем экрана
                    self.turn_left()
                    self.horizontal_velocity = -1

                if self.rect.center[0] - (self.rect.width / 2) <= 0: # столкновение с левым краем экрана
                    self.turn_right()
                    self.horizontal_velocity = 1

            if self.jump_progress <= 0:
                self.falling = True
                self.jumping = False
                self.fall()

        if self.falling:
            self.rect.move_ip(0, 5)

            if self.horizontal_velocity == 1:
                self.rect.move_ip(4, 0)
            if self.horizontal_velocity == -1:
                self.rect.move_ip(-4, 0)

            if self.rect.center[0] + (self.rect.width / 2) >= DISPLAY_WIDTH:  # столкновение с правым краем экрана
                self.turn_left()
                self.horizontal_velocity = -1

            if self.rect.center[0] - (self.rect.width / 2) <= 0:  # столкновение с левым краем экрана
                self.turn_right()
                self.horizontal_velocity = 1

            if self.rect.center[1] + (self.image.get_height() / 2) >= DISPLAY_HEIGHT:
                self.falling = False
                self.rect.center = (self.rect.center[0] , DISPLAY_HEIGHT - (self.image.get_height() / 2))
                self.image = pygame.image.load("textures\\king_idle.png")
                if self.orient_left:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.image = pygame.transform.smoothscale(self.image, (50, 50))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def jump(self):
        texture_jump = pygame.image.load("textures\\king_jump.png")
        texture_jump = pygame.transform.smoothscale(texture_jump, (50, 50))
        if self.orient_left:
            texture_jump = pygame.transform.flip(texture_jump, True, False)
        self.image = texture_jump
        self.jumping = True

    def fall(self):
        texture_fall = pygame.image.load("textures\\king_fall.png")
        if not self.orient_left:
            texture_fall = pygame.transform.flip(texture_fall, True, False)
        texture_fall = pygame.transform.smoothscale(texture_fall, (43.75, 50))
        self.image = texture_fall

    def turn_left(self):
        self.orient_left = True
        texture_idle = pygame.image.load("textures\\king_idle.png")
        texture_idle = pygame.transform.smoothscale(texture_idle, (50, 50))
        self.image = pygame.transform.flip(texture_idle, True, False)

    def turn_right(self):
        self.orient_left = False
        texture_idle = pygame.image.load("textures\\king_idle.png")
        self.image = pygame.transform.smoothscale(texture_idle, (50, 50))



def gameloop(timer):
    timer += 1

    # START OF GAME LOGIC

    P1.update()

    # END OF GAME LOGIC

    DISPLAYSURF.fill(WHITE)
    P1.draw(DISPLAYSURF)
    J1.draw(DISPLAYSURF, J1.jump_progress)

    pygame.display.update()
    return timer

P1 = Player()
J1 = JumpBar()

timer: int = 0
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    timer = gameloop(timer)
    FPS.tick(60)
