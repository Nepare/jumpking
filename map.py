import sys
import time
import math
import json

import pygame
from pygame.locals import *

from map_objects import CollisionObject, TiltObject

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 700

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

class MapController:
    level_list: list = []

    def add_in_order(self, level_in):
        self.level_list.append(level_in)