import pygame
import os

# Import images
gray_tile_img = pygame.transform.scale(pygame.image.load(os.path.join("gray_tile.png")), (20, 20))
water_tile_img = pygame.transform.scale(pygame.image.load(os.path.join("water_tile.png")), (20, 20))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("background.png")), (960, 540))
spinner_img = pygame.transform.scale(pygame.image.load(os.path.join("spinner.png")), (30, 30))

class Room:
    # Pre-blits the ground tile to a separate screen for optimization
    surface = pygame.Surface((20, 20))
    surface.blit(gray_tile_img, (0, 0))
    # Tile types
    GROUND = 0
    WATER = 1
    PLR_SPAWN_POS = 2

    def __init__(self, room_number):
        self.room_number = room_number
        self.ground_tiles = []
        self.water_tiles = []
        self.spinners = []
        self.plr_spawn_point = pygame.Vector2(0, 0)
        self.level_surface_thing = pygame.Surface((960, 540))
        self.next_rooms = [0, 0, 0, 0]

    def generate_room_image(self):
        # Create the current room's image based on data for optimization
        self.level_surface_thing.blit(bg_img, (0, 0))
        for tile in self.ground_tiles:
            self.level_surface_thing.blit(self.surface, tile)
        for tile in self.water_tiles:
            self.level_surface_thing.blit(water_tile_img, tile)
        for spinner in self.spinners:
            self.level_surface_thing.blit(spinner_img, pygame.Vector2(spinner.x - 5, spinner.y - 5))

    def draw(self, window):
        # Draw the pre-drawn full level image for optimization
        if self.level_surface_thing:
            window.blit(self.level_surface_thing, (0, 0))