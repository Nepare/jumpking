import sys
import time

import pygame
from pygame.locals import *

from player import  Player
from map import Map, MapController
from map_objects import CollisionObject, TiltObject
from jumpbar import JumpBar

pygame.init()

FPS = pygame.time.Clock()
FPS.tick(60)

music = pygame.mixer.music.load('sounds\\ogg\\menu_music.ogg')
# pygame.mixer.music.play()

WHITE = (255, 255, 255)

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

Level1 = Map("Начало")
Level1.import_from_json("1")

Level2 = Map("Выступ")
Level2.import_from_json("2")

Level3 = Map("Ход")
Level3.import_from_json("3")

Level4 = Map("Лаз")
Level4.import_from_json("4")

Levels = MapController()
Levels.add_in_order(Level1)
Levels.add_in_order(Level2)
Levels.add_in_order(Level3)
Levels.add_in_order(Level4)

P1.update_level(Level1)
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    timer = gameloop(timer)
    FPS.tick(60)
