import pygame


class Tile:

    GROUND = 0
    WATER = 1
    PLR_SPAWN = 2
    ROOM_CHANGE = 3

    WIDTH = 20
    HEIGHT = 20

    def __int__(self, position, color, purpose, value=None):
        self.pos = position
        self.color = color
        self.purpose = purpose
        self.value = value
