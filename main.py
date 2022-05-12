import json
import sys
import time

import pygame
from pygame.locals import *

from player import  Player
from map import Map, MapController
from map_objects import CollisionObject, TiltObject
from jumpbar import JumpBar
from menu import Menu

pygame.init()

FPS = pygame.time.Clock()
FPS.tick(60)

music = pygame.mixer.music.load('sounds\\ogg\\menu_music.ogg')
pygame.mixer.music.play()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 700

DISPLAYSURF = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Jump King на минималках")
pygame.display.set_icon(pygame.image.load("textures\\king_in_air.png"))

def gameloop(timer):
    timer += 1

    P1.update(J1, Levels)

    DISPLAYSURF.fill(WHITE)

    P1.draw(DISPLAYSURF)
    P1.current_level.draw(DISPLAYSURF)
    J1.draw(DISPLAYSURF)
    P1.save(Levels)

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

Level5 = Map("Крыша")
Level5.import_from_json("5")


Levels = MapController()
Levels.add_in_order(Level1)
Levels.add_in_order(Level2)
Levels.add_in_order(Level3)
Levels.add_in_order(Level4)
Levels.add_in_order(Level5)

P1.update_level(Level1)

menu = Menu()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if menu.in_game:
        timer = gameloop(timer)
    else:
        DISPLAYSURF.fill(BLACK)

        if pygame.key.get_pressed()[K_UP]:
            menu.up()
            FPS.tick(10)
        if pygame.key.get_pressed()[K_DOWN]:
            menu.down()
            FPS.tick(10)
        if pygame.key.get_pressed()[K_SPACE]:
            if menu.chosen == 1:
                menu.in_game = True
            if menu.chosen == 2:
                pygame.quit()
                sys.exit()
            if menu.chosen == 0:
                P1.load(Levels)
                P1.update(J1, Levels)
                menu.in_game = True


        menu.update()
        menu.draw(DISPLAYSURF)
        pygame.display.update()
    FPS.tick(60)

