import sys
import json

import pygame
from pygame.locals import *
from map import Map, MapController

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 700

pygame.mixer.init()


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
    Levels: MapController

    def __init__(self):
        super().__init__()
        texture_idle = pygame.image.load("textures\\king_idle.png")
        self.sound_jump = pygame.mixer.Sound("sounds\\ogg\\sounds_jump.ogg")
        self.sound_bump = pygame.mixer.Sound("sounds\\ogg\\sounds_bump.ogg")
        self.sound_fall = pygame.mixer.Sound("sounds\\ogg\\sounds_fall.ogg")
        self.sound_land = pygame.mixer.Sound("sounds\\ogg\\sounds_land.ogg")

        self.image = texture_idle
        self.image = pygame.transform.scale(self.image,(50,50))
        self.rect = self.image.get_rect()
        self.rect.center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT - (self.image.get_height() / 2) - 1)

    def update(self, jumpbar, Levels):
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
                jumpbar.jump_progress = jumpbar.update(jumpbar.jump_progress)
                if self.jump_progress >= 1:
                    self.jump(jumpbar)
                    jumpbar.jump_progress = jumpbar.update(-0.02) # в следующий такт шкала увеличится на 0.02, поэтому так
            else:
                if self.jump_progress > 0.0:
                    self.jump(jumpbar)
                    jumpbar.jump_progress = jumpbar.update(-0.02)
                else:
                    # ----------------------------------------------- WALKING LEFT
                    if pressed_keys[K_LEFT]:
                        self.idle_animation_progress = 0
                        self.dead = False
                        self.turn_left()
                        if not self.if_collides_left(self.current_level):
                            if not self.if_collides_with_a_slider_side(self.current_level):
                                self.rect.move_ip(-2,0)
                        if self.rect.right <= 0:
                            self.rect.left = DISPLAY_WIDTH - 1
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
                        if self.rect.left >= DISPLAY_WIDTH:
                            self.rect.right = 1
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
                if self.rect.left >= DISPLAY_WIDTH:
                    self.rect.right = 1
                if self.rect.right <= 0:
                    self.rect.left = DISPLAY_WIDTH - 1

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
                self.update_level(Levels.level_list[Levels.level_list.index(self.current_level) + 1])
                self.rect.bottom = DISPLAY_HEIGHT

        # ------------------------------------------------------ WHILE FALLING
        if self.falling:
            self.rect.move_ip(4 * self.horizontal_velocity, 5 + self.downwards_velocity)
            self.downwards_velocity += 0.2
            if self.rect.left >= DISPLAY_WIDTH:
                self.rect.right = 1
            if self.rect.right <= 0:
                self.rect.left = DISPLAY_WIDTH - 1
                self.rect.left = DISPLAY_WIDTH - 1

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
                self.update_level(Levels.level_list[Levels.level_list.index(self.current_level) - 1])
                self.rect.bottom = 0

    def land(self):
        self.falling = False
        if self.downwards_velocity < 9:
            self.image = pygame.image.load("textures\\king_idle.png")
            self.sound_land.play()
        else:
            self.image = pygame.image.load("textures\\king_ded.png")
            self.dead = True
            self.sound_fall.play()
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

    def jump(self, jumpbar):
        if self.jump_progress <= 0.25: # это для того, чтобы минимальный прыжок хотя бы отрывал персонажа от земли
            self.jump_progress = 0.25
        jumpbar.update(0.0)
        texture_jump = pygame.image.load("textures\\king_in_air.png")
        texture_jump = pygame.transform.scale(texture_jump, (50, 50))
        if self.orient_left:
            texture_jump = pygame.transform.flip(texture_jump, True, False)
        self.image = texture_jump
        self.jumping = True
        self.sound_jump.play()

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
        self.sound_bump.play()

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

    def save(self, Levels):
        json_dict: dict = {}
        json_dict["map"] = Levels.level_list.index(self.current_level)
        json_dict["x"] = self.rect.center[0]
        json_dict["y"] = self.rect.center[1]
        json_dict["hor_vel"] = self.horizontal_velocity
        json_dict["ver_vel"] = self.downwards_velocity
        json_dict["falling"] = self.falling
        json_dict["jumping"] = self.jumping

        with open("save_state.json", 'w', encoding="utf-8") as f:
            json.dump(json_dict, f)

    def load(self, Levels):
        with open("save_state.json", 'r') as f:
            json_dict = json.loads(f.read())
            self.update_level(Levels.level_list[int(json_dict["map"])])
            self.rect.center = (json_dict["x"], json_dict["y"])
            self.falling = json_dict["falling"]
            self.jumping = json_dict["jumping"]
            self.horizontal_velocity = json_dict["hor_vel"]
            self.downwards_velocity = json_dict["ver_vel"]