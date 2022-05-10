import sys
import time
import math
import json

import pygame
from pygame.locals import *

from player import  Player
from map import Map, MapController, CollisionObject, TiltObject
from jumpbar import JumpBar

pygame.init()

FPS = pygame.time.Clock()
FPS.tick(60)

BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (200,200,200)
BLACK = (0, 0, 0)

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 700

DISPLAYSURF = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Jump King на минималках")

def gameloop(timer):
    timer += 1

    # START OF GAME LOGIC

    P1.update(J1, Levels)

    # END OF GAME LOGIC

    DISPLAYSURF.fill(WHITE)

    P1.draw(DISPLAYSURF)
    P1.current_level.draw(DISPLAYSURF)
    J1.draw(DISPLAYSURF)

    pygame.display.update()
    return timer

P1 = Player()
J1 = JumpBar()

timer: int = 0

# высота прыжка - примерно 200 пикселей

Level1 = Map("Уровень 1")
Level1.import_from_json("1")

Level2 = Map("Уровень 2")
Level2.import_from_json("2")


Levels = MapController()
Levels.add_in_order(Level1)
Levels.add_in_order(Level2)

P1.update_level(Level1)
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    timer = gameloop(timer)
    FPS.tick(60)
