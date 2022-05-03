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
DISPLAY_HEIGHT = 700

DISPLAYSURF = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Jump King на минималках")

class Map:
    objectList: list = []
    slidersList: list = []

    def add_object(self, obj):
        if isinstance(obj,CollisionObject):
            self.objectList.append(obj)
        if isinstance(obj,SlidingObject):
            self.slidersList.append(obj)

    def draw(self, surface):
        for x in self.objectList:
            x.draw(surface)
        for x in self.slidersList:
            x.draw(surface)

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

class SlidingObject(pygame.sprite.Sprite):
    tilt_left: bool
    bottom_point: list = []
    top_point: list = []

    def __init__(self, bottom_x, bottom_y, top_x, top_y):  # так как все объекты скольжения это треугольники с углом 45,
                                                           # то мы можем нарисовать их по двум точкам
        super().__init__()
        self.top_point = [top_x, top_y]
        self.bottom_point = [bottom_x, bottom_y]
        if top_x > bottom_x:                               # если вершина склона справа, то склон идёт влево
            tilt_left = True
        else:
            tilt_left = False

    def draw(self, surface):
        pygame.draw.polygon(surface, BLACK, [(self.bottom_point[0], DISPLAY_HEIGHT - self.bottom_point[1]),
                                (self.top_point[0], DISPLAY_HEIGHT - self.top_point[1]), (self.top_point[0], DISPLAY_HEIGHT - self.bottom_point[1])], 0)


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
        scale = pygame.draw.rect(surface, GREEN, (7, 143 - (self.jump_progress * 138), 36, 138 * self.jump_progress), 20)


class Player(pygame.sprite.Sprite):
    jump_progress: float = 0.0
    falling: bool = False
    jumping: bool = False
    orient_left: bool = False
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
            # ----------------------------------------------- JUMPING
            if pressed_keys[K_SPACE]:
                texture_charging = pygame.image.load("textures\\king_charge.png")
                texture_charging = pygame.transform.scale(texture_charging,(50,50))
                self.image = texture_charging
                self.idle_animation_progress = 0

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
                    J1.jump_progress = J1.update(0)
            else:
                if self.jump_progress > 0.0:
                    self.jump()
                    J1.jump_progress = J1.update(0)
                else:
                    # ----------------------------------------------- WALKING LEFT
                    if pressed_keys[K_LEFT]:
                        self.idle_animation_progress = 0
                        self.turn_left()
                        if not self.rect.center[0] - (self.rect.width / 2) <= 0:
                            if not self.if_collides_left(self.current_level):
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
                        self.turn_right()
                        if not self.rect.center[0] + (self.rect.width / 2) >= DISPLAY_WIDTH:
                            if not self.if_collides_right(self.current_level):
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
                        self.idle_animation_progress += 1
                        if self.idle_animation_progress >= 1000: # 1000 тиков для полного цикла анимации покоя
                            self.idle_animation_progress = 0
                        self.texture_idle_animation()


        # ------------------------------------------------------------- WHILE JUMPING
        if self.jumping:
            if self.jump_progress > 0.0:
                self.rect.move_ip(4 * self.horizontal_velocity, -14 * (self.jump_progress))
                self.jump_progress -= 0.03

                if self.rect.center[0] + (self.rect.width / 2) >= DISPLAY_WIDTH: # столкновение с правым краем экрана
                    self.turn_left()
                    self.texture_bounce()

                if self.rect.center[0] - (self.rect.width / 2) <= 0: # столкновение с левым краем экрана
                    self.turn_right()
                    self.texture_bounce()

            if self.jump_progress <= 0:
                self.falling = True
                self.jumping = False
                self.fall()

            bumping_surface = self.if_collides_up(self.current_level)
            if bumping_surface:
                self.fall()
                self.jump_progress = 0

            bounce_left_surface = self.if_collides_left(self.current_level)
            if bounce_left_surface:
                self.turn_right()
                self.texture_bounce()

            bounce_right_surface = self.if_collides_right(self.current_level)
            if bounce_right_surface:
                self.turn_left()
                self.texture_bounce()

        # ------------------------------------------------------ WHILE FALLING
        if self.falling:
            self.rect.move_ip(4 * self.horizontal_velocity, 5 + self.downwards_velocity)
            self.downwards_velocity += 0.2

            if self.rect.center[0] + (self.rect.width / 2) >= DISPLAY_WIDTH:  # столкновение с правым краем экрана
                self.turn_left()
                self.texture_fall()

            if self.rect.center[0] - (self.rect.width / 2) <= 0:  # столкновение с левым краем экрана
                self.turn_right()
                self.texture_fall()

            bounce_left_surface = self.if_collides_left(self.current_level)
            if bounce_left_surface:
                self.turn_right()
                self.texture_bounce()

            bounce_right_surface = self.if_collides_right(self.current_level)
            if bounce_right_surface:
                self.turn_left()
                self.texture_bounce()

            if self.rect.center[1] + (self.image.get_height() / 2) >= DISPLAY_HEIGHT:
                self.land()
                self.rect.center = (self.rect.center[0], DISPLAY_HEIGHT - (self.image.get_height() / 2))

            standing_surface = self.if_collides_down(self.current_level)
            if standing_surface:
                self.land()
                self.move_to_top_surface(self.current_level, standing_surface)

    def land(self):
        self.falling = False
        self.image = pygame.image.load("textures\\king_idle.png")
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
            if self.rect.top <= DISPLAY_HEIGHT - object.bottom_left[1] and self.rect.top >= (DISPLAY_HEIGHT - object.bottom_left[1] - 5 - self.downwards_velocity):
                if self.rect.left <= object.top_right[0] and self.rect.right >= object.bottom_left[0]:
                    return object
        return False

    def if_collides_left(self, current_level):
        if not self.orient_left:
            return False
        for object in current_level.objectList:
            if self.rect.left >= object.bottom_left[0] and self.rect.left <= object.top_right[0]:
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
            if self.rect.right >= object.bottom_left[0] and self.rect.right <= object.top_right[0]:
                if DISPLAY_HEIGHT - object.bottom_left[1] < self.rect.bottom and DISPLAY_HEIGHT - object.bottom_left[1] > self.rect.top:
                    return object
                if DISPLAY_HEIGHT - object.top_right[1] < self.rect.bottom and DISPLAY_HEIGHT - object.top_right[1] > self.rect.top:
                    return object
                if DISPLAY_HEIGHT - object.top_right[1] <= self.rect.top and DISPLAY_HEIGHT - object.bottom_left[1] >= self.rect.bottom:
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
    current_level = Level1
    timer += 1

    # START OF GAME LOGIC

    P1.update()

    # END OF GAME LOGIC

    DISPLAYSURF.fill(WHITE)

    P1.draw(DISPLAYSURF)
    J1.draw(DISPLAYSURF)
    current_level.draw(DISPLAYSURF)

    pygame.display.update()
    return timer

P1 = Player()
J1 = JumpBar()
Level1 = Map()
P1.update_level(Level1)

timer: int = 0

# высота прыжка - примерно 200 пикселей

Level1.add_object(CollisionObject(0,0,DISPLAY_WIDTH,1)) # это пол, по котором ходит персонаж
Level1.add_object(CollisionObject(250,140,450,180))
Level1.add_object(CollisionObject(0,0,20,20))
Level1.add_object(CollisionObject(100,300,200,340))
Level1.add_object(CollisionObject(180,340,200,360))
Level1.add_object(CollisionObject(240,460,350,500))
Level1.add_object(CollisionObject(280,460,330,600))
Level1.add_object(CollisionObject(520,340,600,380))
Level1.add_object(CollisionObject(100,600,200,640))
# Level1.add_object(SlidingObject(20,0,40,20))

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    timer = gameloop(timer)
    FPS.tick(60)
