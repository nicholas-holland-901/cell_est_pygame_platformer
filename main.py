import pygame
import player
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


# Snap to tile grid
def round_to_tile(mouse_pos):
    x = 0
    y = 0
    # Get tile horizontally
    for i in range(48):
        if i * 20 <= mouse_pos[0] <= i * 20 + 20:
            x = i * 20
    # Get tile vertically
    for i in range(27):
        if i * 20 <= mouse_pos[1] <= i * 20 + 20:
            y = i * 20
    return x, y


# Buttons to control the level editor
def edit_buttons():
    global tile_type

    # Draw background for button area
    pygame.draw.rect(screen, (50, 50, 50), [0, HEIGHT - 49, WIDTH, 49])

    # Draw border on the top of the button area
    pygame.draw.rect(screen, (255, 255, 255), [0, HEIGHT - 50, WIDTH, 1])

    # Buttons
    ground_tile_button = pygame.draw.rect(screen, (100, 100, 100), [10, HEIGHT - 40, 30, 30])
    water_tile_button = pygame.draw.rect(screen, water_color, [50, HEIGHT - 40, 30, 30])
    plr_spawn_point_button = pygame.draw.rect(screen, (255, 100, 100), [90, HEIGHT - 40, 30, 30])
    change_tile_button = pygame.draw.rect(screen, (255, 255, 255), [130, HEIGHT - 40, 30, 30])

    level_change_button = pygame.draw.rect(screen, (255, 255, 255), [920, HEIGHT - 40, 30, 30])

    mouse_press = pygame.mouse.get_pressed()
    if mouse_press[0]:
        mouse_pos = pygame.mouse.get_pos()
        if in_region(ground_tile_button, mouse_pos):
            tile_type = TileType.ground
        elif in_region(water_tile_button, mouse_pos):
            tile_type = TileType.water
        elif in_region(plr_spawn_point_button, mouse_pos):
            tile_type = TileType.plr_spawn_pos
        elif in_region(level_change_button, mouse_pos):
            tile_type = TileType.room_transition


# Generate room code that can be used to load to level and save the layout
def generate_room_code():
    room_save_code = str(room) + ":"
    tile_code = ""
    # Add the ground tiles already in the room
    for tile in all_tiles:
        tile_code = str(tile[0].x) + "/" + str(tile[0].y) + "&" + str(tile[1]) + "#"
        room_save_code += tile_code
    # Draw player spawn point
    room_save_code += str(int(player_spawn_point.x)) + "/" + str(int(player_spawn_point.y)) + "&2#"

    # Remove the hashtag from the end of the room code
    room_save_code = room_save_code[:-1]

    file = open("map_layout", 'r')
    lines = file.readlines()

    return room_save_code


# Draw all tiles
def draw_all_tiles():
    for tile in ground_tiles:
        pygame.draw.rect(screen, (100, 100, 100), tile)
    for tile in water_tiles:
        pygame.draw.rect(screen, water_color, tile)


# Edit mode to add tiles to level
while edit_mode:
    screen.fill(screen_color)
    draw_water()
    pygame.draw.rect(screen, (255, 100, 100), [player_spawn_point.x, player_spawn_point.y, 20, 20])
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            # Save the current room
            room_code = generate_room_code()
            file = open("map_layout", 'r')
            lines = file.readlines()
            w = open("map_layout", "w")
            exists = False
            for line in lines:
                if int(line[:1]) == room:
                    exists = True
                    i = lines.index(line)
                    lines[i] = room_code
                    if not i == len(lines) - 1:
                        lines[i] = room_code + "\n"
                    w.writelines(lines)
            if not exists:
                # Room didn't already exist
                lines.append("\n" + room_code)
                w.writelines(lines)
            w.close()
            quit()

    # Edit mode GUI
    edit_buttons()

    # Get mouse input
    mouse_press = pygame.mouse.get_pressed()
    if mouse_press[0] and pygame.mouse.get_pos()[1] < 540:
        # Place tile on left click
        mouse = round_to_tile(pygame.mouse.get_pos())
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
        mouse = round_to_tile(pygame.mouse.get_pos())
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
