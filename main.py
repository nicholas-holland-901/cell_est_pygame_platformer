import pygame
import player
import runtime_editor
from enum import Enum

autoload = True
edit_mode = False
all_tiles = []

if edit_mode:
    # Window dimensions
    WIDTH = 960
    HEIGHT = 590
else:
    # Window dimensions
    WIDTH = 960
    HEIGHT = 540

pygame.init()

clock = pygame.time.Clock()

# Colors
tile_color = (100, 100, 100)
water_color = (75, 75, 255)


# Different types of tiles that can exist
class TileType(Enum):
    ground = 0
    water = 1
    plr_spawn_pos = 2
    room_transition = 3


# The current room being drawn on the screen
room = 0
next_room = 0

tile_type = TileType.ground

player_spawn_point = pygame.Vector2(300, 400)

# Tile types
ground_tiles = []
water_tiles = []
change_tiles = []

# Window title
pygame.display.set_caption("Pygame")

# Background color
screen_color = (15, 15, 15)
default_player_color = (255, 100, 100)
no_dash_player_color = (100, 100, 255)

# Set window size
screen = pygame.display.set_mode((WIDTH, HEIGHT))

tiles = [pygame.Rect(0, HEIGHT - 50, WIDTH, 50), pygame.Rect(500, 400, 30, 30), pygame.Rect(300, 400, 30, 70)]


def player_setup():
    global player
    player = player.Player(screen, 0, 0)
    player.ground_tiles = ground_tiles
    player.water_tiles = water_tiles


if autoload:
    f = open("map_layout", "a")
    f.close()
    r = open("map_layout", "r")
    data = r.readlines()
    if data:
        for line in data:
            if int(line[:1]) == room:
                data = data[data.index(line)]
                data = data.split(":")
                data = data[1].split("#")
                for tile_data in data:
                    values = tile_data.split("&")
                    if "\n" in values[1]:
                        values[1] = values[1][:1]
                    position = values[0].split("/")
                    x = int(position[0])
                    y = int(position[1])
                    all_tiles.append((pygame.Rect(x, y, 20, 20), values[1]))
                    version = int(values[1])
                    if version == 0:
                        # Ground tile
                        ground_tiles.append(pygame.Rect(x, y, 20, 20))
                    elif version == 1:
                        # Water tile
                        water_tiles.append(pygame.Rect(x, y, 20, 20))
                    elif version == 2:
                        # Player spawn point
                        player_spawn_point.x = x
                        player_spawn_point.y = y
                        player.pos.x = x
                        player.pos.y = y


# Used for buttons to see if the mouse cursor is in the rect
def in_region(rectangle, pos):
    if rectangle.x < pos[0] < rectangle.right and rectangle.y < pos[1] < rectangle.bottom:
        return True
    else:
        return False


# Draw the water tiles
def draw_water():
    for tile in water_tiles:
        pygame.draw.rect(screen, water_color, tile)


# Normal runtime behaviour
while not edit_mode:
    screen.fill(screen_color)
    draw_water()
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            quit()

    player.update()

    pygame.display.update()

    clock.tick(60)

# Draw all tiles
def draw_all_tiles():
    for tile in ground_tiles:
        pygame.draw.rect(screen, tile_color, tile)
    for tile in water_tiles:
        pygame.draw.rect(screen, water_color, tile)


# Loop for when editing
while edit_mode:
    screen.fill(screen_color)
    draw_water()
    pygame.draw.rect(screen, (255, 100, 100), [player_spawn_point.x, player_spawn_point.y, 20, 20])
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            # Save the current room before closing
            runtime_editor.save_layout()
            quit()

    # Edit mode GUI
    runtime_editor.edit_buttons()

    # Get mouse input
    mouse_press = pygame.mouse.get_pressed()
    if mouse_press[0] and pygame.mouse.get_pos()[1] < 540:
        # Place tile on left click
        mouse = runtime_editor.round_to_tile(pygame.mouse.get_pos())
        tile_rect = pygame.Rect(mouse[0], mouse[1], 20, 20)
        new_tile = (tile_rect, tile_type.value)
        if new_tile not in all_tiles:
            if tile_type.value != 2:
                all_tiles.append(new_tile)
            if tile_type.value == 0:
                ground_tiles.append(tile_rect)
            elif tile_type.value == 1:
                water_tiles.append(tile_rect)
            elif tile_type.value == 2:
                player_spawn_point.x = tile_rect.x
                player_spawn_point.y = tile_rect.y
            elif tile_type.value == 3:
                change_tiles.append([tile_rect, next_room])
    if mouse_press[2] and pygame.mouse.get_pos()[1] < 540:
        # Delete tile on right click
        mouse = runtime_editor.round_to_tile(pygame.mouse.get_pos())
        tile_rect = pygame.Rect(mouse[0], mouse[1], 20, 20)
        new_tile = (tile_rect, tile_type.value)
        if new_tile in all_tiles:
            all_tiles.remove(new_tile)
            if tile_type.value == 0:
                ground_tiles.remove(tile_rect)
            elif tile_type.value == 1:
                water_tiles.remove(tile_rect)
            elif tile_type.value == 2:
                all_tiles.remove(new_tile)
            elif tile_type.value == 3:
                change_tiles.remove([tile_rect, next_room])

    # Draw all the tiles
    draw_all_tiles()

    pygame.display.update()
