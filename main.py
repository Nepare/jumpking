import sys
import time
import math
import json

import pygame
from pygame.locals import *

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

class Map:
    objectList: list = []
    tiltList: list = []
    name: str

    def __init__(self, name_in):
        self.name = name_in
        self.objectList = []
        self.tiltList = []

    def add_object(self, obj):
        if isinstance(obj,CollisionObject):
            self.objectList.append(obj)
        if isinstance(obj,TiltObject):
            self.tiltList.append(obj)

    def draw(self, surface):
        for x in self.objectList:
            x.draw(surface)
        for x in self.tiltList:
            x.draw(surface)

    def import_from_json(self, json_file_name):
        with open("levels\\" + json_file_name + ".json", 'r') as f:
            level_dict = json.load(f)
            collision_objects = level_dict["col"]
            tilt_objects = level_dict["tilt"]
            for x in collision_objects:
                self.add_object(CollisionObject(*x))
            if tilt_objects:
                for x in tilt_objects:
                    self.add_object(TiltObject(*x))

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

class MapController:
    level_list: list = []

    def add_in_order(self, level_in):
        self.level_list.append(level_in)

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
        border = pygame.draw.rect(DISPLAYSURF, BLACK, (5, 5, 40, 140), 2)
        border = pygame.draw.rect(DISPLAYSURF, GRAY, (7, 7, 36, 136), 0)
        scale = pygame.draw.rect(surface, GREEN, (7, 143 - (self.jump_progress * 138), 36, 138 * self.jump_progress), 20)

class Player(pygame.sprite.Sprite):
    jump_progress: float = 0.0
    falling: bool = False
    jumping: bool = False
    orient_left: bool = False
    dead: bool = False
    horizontal_velocity: int = 0
    downwards_velocity: float = 0.0
    walk_animation_progress: int = 0
    idle_animation_progress: int = 0
    current_level: Map

    def __init__(self):
        super().__init__()
        texture_idle = pygame.image.load("textures\\king_idle.png")

        self.image = texture_idle
        self.image = pygame.transform.scale(self.image,(50,50))
        self.rect = self.image.get_rect()
        self.rect.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - (self.image.get_height() / 2) - 1)

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        if not self.jumping and not self.falling:
            # ----------------------------------------------- CHARGING A JUMP
            if pressed_keys[K_SPACE]:
                texture_charging = pygame.image.load("textures\\king_charge.png")
                texture_charging = pygame.transform.scale(texture_charging,(50,50))
                self.image = texture_charging
                self.idle_animation_progress = 0
                self.dead = False

                if pressed_keys[K_RIGHT]:
                    self.turn_right()
                elif pressed_keys[K_LEFT]:
                    self.turn_left()
                else:
                    self.horizontal_velocity = 0
                    self.walk_animation_progress = 0

                self.jump_progress += 0.02
                J1.jump_progress = J1.update(J1.jump_progress)
                if self.jump_progress >= 1:
                    self.jump()
                    J1.jump_progress = J1.update(-0.02) # в следующий такт шкала увеличится на 0.02, поэтому так
            else:
                if self.jump_progress > 0.0:
                    self.jump()
                    J1.jump_progress = J1.update(-0.02)
                else:
                    # ----------------------------------------------- WALKING LEFT
                    if pressed_keys[K_LEFT]:
                        self.idle_animation_progress = 0
                        self.dead = False
                        self.turn_left()
                        if not self.if_collides_left(self.current_level):
                            if not self.if_collides_with_a_slider_side(self.current_level):
                                self.rect.move_ip(-2,0)
                        self.walk_animation_progress += 1
                        if self.walk_animation_progress >= 40:
                            self.walk_animation_progress = 0
                        self.texture_walk()
                        if not self.if_collides_down(self.current_level):
                            self.falling = True
                            self.fall()
                    # ----------------------------------------------- WALKING RIGHT
                    elif pressed_keys[K_RIGHT]:
                        self.idle_animation_progress = 0
                        self.dead = False
                        self.turn_right()
                        if not self.if_collides_right(self.current_level):
                            if not self.if_collides_with_a_slider_side(self.current_level):
                                self.rect.move_ip(2,0)
                        self.walk_animation_progress += 1
                        if self.walk_animation_progress >= 40:
                            self.walk_animation_progress = 0
                        self.texture_walk()
                        if not self.if_collides_down(self.current_level):
                            self.falling = True
                            self.fall()
                    # ----------------------------------------------- NOTHING HAPPENS
                    else:
                        if not self.dead:
                            self.idle_animation_progress += 1
                            if self.idle_animation_progress >= 1000: # 1000 тиков для полного цикла анимации покоя
                                self.idle_animation_progress = 0
                            self.texture_idle_animation()


        # ------------------------------------------------------------- WHILE JUMPING
        if self.jumping:
            if self.jump_progress > 0.0:
                self.rect.move_ip(4 * self.horizontal_velocity, -14 * (self.jump_progress))
                self.jump_progress -= 0.03

            if self.jump_progress <= 0:
                self.falling = True
                self.jumping = False
                self.fall()

            if self.if_collides_up(self.current_level):
                self.fall()
                self.jump_progress = 0
            elif self.if_collides_left(self.current_level) and self.horizontal_velocity != 0:
                self.turn_right()
                self.texture_bounce()
            elif self.if_collides_right(self.current_level) and self.horizontal_velocity != 0:
                self.turn_left()
                self.texture_bounce()

            current_slider = self.if_collides_with_a_slider_tilt(self.current_level)
            if current_slider:
                relative_x: int
                if current_slider.tilt_left:
                    touching_point = self.rect.bottomright
                    relative_x = touching_point[0] - current_slider.left_x
                else:
                    touching_point = self.rect.bottomleft
                    relative_x = current_slider.right_x - touching_point[0]
                self.rect.move_ip(0,(-1) * (relative_x - (DISPLAY_HEIGHT - current_slider.bottom_point[1] - self.rect.bottom)))
                # ^ если мы прыгаем вверх по горке, мы именно что скользим по прямой горке, а не дуге в горку

            if self.rect.bottom <= 0:
                P1.update_level(Levels.level_list[Levels.level_list.index(self.current_level) + 1])
                self.rect.bottom = DISPLAY_HEIGHT

        # ------------------------------------------------------ WHILE FALLING
        if self.falling:
            self.rect.move_ip(4 * self.horizontal_velocity, 5 + self.downwards_velocity)
            self.downwards_velocity += 0.2

            if self.if_collides_left(self.current_level) and self.horizontal_velocity != 0:
                self.turn_right()
                self.texture_bounce()
            elif self.if_collides_right(self.current_level) and self.horizontal_velocity != 0:
                self.turn_left()
                self.texture_bounce()

            standing_surface = self.if_collides_down(self.current_level)
            if standing_surface:
                self.land()
                self.move_to_top_surface(self.current_level, standing_surface)

            current_slider = self.if_collides_with_a_slider_tilt(self.current_level)
            if current_slider:
                if current_slider.tilt_left:
                    self.turn_left()
                else:
                    self.turn_right()
                self.texture_bounce()
                relative_x: int
                if current_slider.tilt_left:
                    touching_point = self.rect.bottomright
                    relative_x = touching_point[0] - current_slider.left_x
                else:
                    touching_point = self.rect.bottomleft
                    relative_x = current_slider.right_x - touching_point[0]
                self.rect.move_ip(self.horizontal_velocity, (-1) * (relative_x - (DISPLAY_HEIGHT - current_slider.bottom_point[1] - self.rect.bottom)))

            if self.rect.bottom >= DISPLAY_HEIGHT:
                P1.update_level(Levels.level_list[Levels.level_list.index(self.current_level) - 1])
                self.rect.bottom = 0

    def land(self):
        self.falling = False
        if self.downwards_velocity < 9:
            self.image = pygame.image.load("textures\\king_idle.png")
        else:
            self.image = pygame.image.load("textures\\king_ded.png")
            self.dead = True
        self.downwards_velocity = 0.0
        if self.orient_left:
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (50, 50))

    def if_collides_down(self, current_level):
        for object in current_level.objectList:
            if self.rect.bottom >= DISPLAY_HEIGHT - object.top_right[1] and self.rect.bottom <= DISPLAY_HEIGHT - \
                    (object.top_right[1] - 5 - self.downwards_velocity): # Если низ персонажа находится НИЖЕ чем
                                                                         # верхняя грань объекта, но выше чем
                                                                         # нижняя грань куда он может провалиться
                                                                         # (т.е. если он застрял в текстурах)
                if self.rect.left + 9 <= object.top_right[0] and self.rect.right - 9 >= object.bottom_left[0]:
                    return object
        return False

    def move_to_top_surface(self, current_level, standing_surface):
            self.rect.move_ip(0,(-1) * (self.rect.bottom - (DISPLAY_HEIGHT - standing_surface.top_right[1])))

    def if_collides_up(self, current_level):
        for object in current_level.objectList:
            if self.rect.top <= DISPLAY_HEIGHT - object.bottom_left[1] and self.rect.top >= (DISPLAY_HEIGHT - object.bottom_left[1] - 14):
                if self.rect.left <= object.top_right[0] and self.rect.right >= object.bottom_left[0]:
                    return object
        for object in current_level.tiltList:
            if self.rect.top <= DISPLAY_HEIGHT - object.bottom_point[1] and self.rect.top >= (DISPLAY_HEIGHT - object.bottom_point[1] - 14):
                if self.rect.left <= object.right_x and self.rect.right >= object.left_x:
                    return object
        return False

    def if_collides_left(self, current_level):
        if not self.orient_left:
            return False
        for object in current_level.objectList:
            if self.rect.left >= object.top_right[0] - 8 and self.rect.left <= object.top_right[0]:
                                                                    # 8 пикселей - это максимальная глубина застревания
                if DISPLAY_HEIGHT - object.bottom_left[1] < self.rect.bottom and DISPLAY_HEIGHT - object.bottom_left[1] > self.rect.top:
                    return object
                if DISPLAY_HEIGHT - object.top_right[1] < self.rect.bottom and DISPLAY_HEIGHT - object.top_right[1] > self.rect.top:
                    return object
                if DISPLAY_HEIGHT - object.top_right[1] <= self.rect.top and DISPLAY_HEIGHT - object.bottom_left[1] >= self.rect.bottom:
                    return object
        return False

    def if_collides_right(self, current_level):
        if self.orient_left:
            return False
        for object in current_level.objectList:
            if self.rect.right >= object.bottom_left[0] and self.rect.right <= object.bottom_left[0] + 8:
                                                                    # 8 пикселей - это максимальная глубина застревания
                if DISPLAY_HEIGHT - object.bottom_left[1] < self.rect.bottom and DISPLAY_HEIGHT - object.bottom_left[1] > self.rect.top:
                    return object
                if DISPLAY_HEIGHT - object.top_right[1] < self.rect.bottom and DISPLAY_HEIGHT - object.top_right[1] > self.rect.top:
                    return object
                if DISPLAY_HEIGHT - object.top_right[1] <= self.rect.top and DISPLAY_HEIGHT - object.bottom_left[1] >= self.rect.bottom:
                    return object
        return False

    def if_collides_with_a_slider_side(self, current_level):
        if self.orient_left:
            for object in current_level.tiltList:
                if self.rect.left <= object.right_x and self.rect.left >= object.right_x - 6:
                    if self.rect.top > DISPLAY_HEIGHT - object.top_point[1] and self.rect.top < DISPLAY_HEIGHT - object.bottom_point[1]:
                        return True
                    if self.rect.bottom > DISPLAY_HEIGHT - object.top_point[1] and self.rect.bottom < DISPLAY_HEIGHT - object.bottom_point[1]:
                        return True
                    if self.rect.top < DISPLAY_HEIGHT - object.top_point[1] and self.rect.bottom > DISPLAY_HEIGHT - object.top_point[1]:
                        return True
        else:
            for object in current_level.tiltList:
                if self.rect.right >= object.left_x and self.rect.right <= object.left_x + 6:
                    if self.rect.top > DISPLAY_HEIGHT - object.top_point[1] and self.rect.top < DISPLAY_HEIGHT - \
                            object.bottom_point[1]:
                        return True
                    if self.rect.bottom > DISPLAY_HEIGHT - object.top_point[1] and self.rect.bottom < DISPLAY_HEIGHT - \
                            object.bottom_point[1]:
                        return True
                    if self.rect.top < DISPLAY_HEIGHT - object.top_point[1] and self.rect.bottom > DISPLAY_HEIGHT - \
                            object.top_point[1]:
                        return True
        return False

    def if_collides_with_a_slider_tilt(self, current_level):
        touching_point: list = []

        for object in current_level.tiltList:
            relative_x: int
            if object.tilt_left:
                touching_point = self.rect.bottomright
                relative_x = touching_point[0] - object.left_x
            else:
                touching_point = self.rect.bottomleft
                relative_x = object.right_x - touching_point[0]

            if touching_point[0] >= object.left_x - 1 and touching_point[0] <= object.right_x + 1: # если игрок над/под склоном
                if touching_point[1] > DISPLAY_HEIGHT - (object.bottom_point[1] + relative_x) and touching_point[1] < \
                        DISPLAY_HEIGHT - (object.bottom_point[1] + relative_x - 25):
                    return object

        return False


    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def jump(self):
        if self.jump_progress <= 0.25: # это для того, чтобы минимальный прыжок хотя бы отрывал персонажа от земли
            self.jump_progress = 0.25
        J1.update(0.0)
        texture_jump = pygame.image.load("textures\\king_in_air.png")
        texture_jump = pygame.transform.scale(texture_jump, (50, 50))
        if self.orient_left:
            texture_jump = pygame.transform.flip(texture_jump, True, False)
        self.image = texture_jump
        self.jumping = True

    def fall(self):
        self.downwards_velocity = 0.0
        texture_fall = pygame.image.load("textures\\king_fall.png")
        if self.orient_left:
            texture_fall = pygame.transform.flip(texture_fall, True, False)
        texture_fall = pygame.transform.scale(texture_fall, (50, 50))
        self.image = texture_fall

    def turn_left(self):
        self.orient_left = True
        self.horizontal_velocity = -1

    def turn_right(self):
        self.orient_left = False
        self.horizontal_velocity = 1

    def texture_bounce(self):
        texture_bounce = pygame.image.load("textures\\king_bounce.png")
        texture_bounce = pygame.transform.scale(texture_bounce, (50, 50))
        self.image = texture_bounce
        if not self.orient_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def texture_fall(self):
        texture_fall = pygame.image.load("textures\\king_fall.png")
        texture_fall = pygame.transform.scale(texture_fall, (50, 50))
        self.image = texture_fall
        if self.orient_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def texture_walk(self):
        texture_walk = self.image
        if self.walk_animation_progress > 0 and self.walk_animation_progress < 11:
            texture_walk = pygame.image.load("textures\\king_walk_1.png")
        if self.walk_animation_progress > 10 and self.walk_animation_progress < 21:
            texture_walk = pygame.image.load("textures\\king_walk_2.png")
        if self.walk_animation_progress > 20 and self.walk_animation_progress < 31:
            texture_walk = pygame.image.load("textures\\king_walk_3.png")
        if self.walk_animation_progress > 30 and self.walk_animation_progress < 41:
            texture_walk = pygame.image.load("textures\\king_walk_2.png")
        texture_walk = pygame.transform.scale(texture_walk, (50, 50))
        self.image = texture_walk
        if self.orient_left:
            self.image = pygame.transform.flip(self.image, True, False)

    # ---------------------------------- IDLE ANIMATIONS
    def texture_idle_animation(self):
        texture_idle = self.image
        if self.idle_animation_progress > 0 and self.idle_animation_progress < 301:
            texture_idle = pygame.image.load("textures\\king_idle.png")
        for i in range(2):
            if self.idle_animation_progress > 300 + 80*i and self.idle_animation_progress < 321 + 80*i:
                texture_idle = pygame.image.load("textures\\king_warming_up_1.png")
            if self.idle_animation_progress > 320 + 80*i and self.idle_animation_progress < 341 + 80*i:
                texture_idle = pygame.image.load("textures\\king_warming_up_2.png")
            if self.idle_animation_progress > 340 + 80*i and self.idle_animation_progress < 361 + 80*i:
                texture_idle = pygame.image.load("textures\\king_warming_up_3.png")
            if self.idle_animation_progress > 360 + 80*i and self.idle_animation_progress < 381 + 80*i:
                texture_idle = pygame.image.load("textures\\king_warming_up_2.png")
            if self.idle_animation_progress > 380 + 80*i and self.idle_animation_progress < 401 + 80*i:
                texture_idle = pygame.image.load("textures\\king_warming_up_1.png")
        if self.idle_animation_progress > 480 and self.idle_animation_progress < 801:
            texture_idle = pygame.image.load("textures\\king_idle.png")
        if self.idle_animation_progress > 800 and self.idle_animation_progress < 1001:
            texture_idle = pygame.image.load("textures\\king_look_up.png")

        texture_idle = pygame.transform.scale(texture_idle, (50, 50))
        self.image = texture_idle
        if self.orient_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def update_level(self, new_level):
        self.current_level = new_level



def gameloop(timer):
    timer += 1

    # START OF GAME LOGIC

    P1.update()

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
