import pygame
import os

# Import images
gray_tile_img = pygame.transform.scale(pygame.image.load(os.path.join("gray_tile.png")), (20, 20))

class Room:

    # Tile types
    GROUND = 0
    WATER = 1
    PLR_SPAWN_POS = 2

    def __init__(self, room_number):
        self.room_number = room_number
        self.ground_tiles = []
        self.water_tiles = []
        self.plr_spawn_point = pygame.Vector2(0, 0)
        self.next_rooms = [0, 0, 0, 0]

    def draw(self, window):
        for tile in self.ground_tiles:
            # pygame.draw.rect(window, (100, 100, 100), tile)
            window.blit(gray_tile_img, tile)
        for tile in self.water_tiles:
            pygame.draw.rect(window, (0, 0, 100), tile)