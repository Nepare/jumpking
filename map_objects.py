import sys

import pygame
from pygame.locals import *

BLACK = (0, 0, 0)

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 700

class CollisionObject(pygame.sprite.Sprite):
    x_border: list = []
    y_border: list = []
    obj_width: int
    obj_height: int

    def __init__(self, bottom_left_x, bottom_left_y, top_right_x, top_right_y):
        super().__init__()
        self.bottom_left = [bottom_left_x, bottom_left_y]
        self.top_right = [top_right_x, top_right_y]
        self.obj_width = top_right_x - bottom_left_x
        self.obj_height = top_right_y - bottom_left_y


    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, (self.bottom_left[0], DISPLAY_HEIGHT - self.top_right[1], self.obj_width, self.obj_height), 0 )

class TiltObject(pygame.sprite.Sprite):
    tilt_left: bool
    bottom_point: list = []
    top_point: list = []
    right_x: int
    left_x: int

    def __init__(self, bottom_x, bottom_y, top_x, top_y):  # так как все объекты скольжения это треугольники с углом 45,
                                                           # то мы можем нарисовать их по двум точкам
        super().__init__()
        self.top_point = [top_x, top_y]
        self.bottom_point = [bottom_x, bottom_y]
        if top_x > bottom_x:                               # если вершина склона справа, то склон идёт влево (и вниз)
            self.tilt_left = True
            self.right_x = top_x
            self.left_x = bottom_x
        else:
            self.tilt_left = False
            self.right_x = bottom_x
            self.left_x = top_x

    def draw(self, surface):
        pygame.draw.polygon(surface, BLACK, [(self.bottom_point[0], DISPLAY_HEIGHT - self.bottom_point[1]),
                                (self.top_point[0], DISPLAY_HEIGHT - self.top_point[1]), (self.top_point[0], DISPLAY_HEIGHT - self.bottom_point[1])], 0)
