import pygame
import os

# Import images
gray_tile_img = pygame.transform.scale(pygame.image.load(os.path.join("gray_tile.png")), (20, 20))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("background.png")), (960, 540))

class Room:

    surface = pygame.Surface((20, 20))
    surface.blit(gray_tile_img, (0, 0))
    # Tile types
    GROUND = 0
    WATER = 1
    PLR_SPAWN_POS = 2
    level_surface_thing = None

    def __init__(self, room_number):
        self.room_number = room_number
        self.ground_tiles = []
        self.water_tiles = []
        self.plr_spawn_point = pygame.Vector2(0, 0)
        self.next_rooms = [0, 0, 0, 0]

    def draw(self, window):
        if not self.level_surface_thing:
            self.level_surface_thing = pygame.Surface((960, 540))
            self.level_surface_thing.blit(bg_img, (0, 0))
            # window.blit(bg_img, (0, 0))
            for tile in self.ground_tiles:
                # pygame.draw.rect(window, (100, 100, 100), tile)
                # window.blit(self.surface, tile)
                self.level_surface_thing.blit(self.surface, tile)
            for tile in self.water_tiles:
                # pygame.draw.rect(window, (0, 0, 100), tile)
                pass
        else:
            window.blit(self.level_surface_thing, (0, 0))