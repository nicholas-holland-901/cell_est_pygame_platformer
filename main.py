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
    # Window dimension
    WIDTH = 960
    HEIGHT = 540

pygame.init()

clock = pygame.time.Clock()

first_load = True

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
# Up down left right
next_room = [0, 0, 0, 0]

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
    global plr
    plr = player.Player(screen, 0, 0)
    plr.ground_tiles = ground_tiles
    plr.water_tiles = water_tiles

player_setup()

def clear_room():
    global ground_tiles, water_tiles, all_tiles, first_load

    ground_tiles = []
    water_tiles = []
    all_tiles = []
    if first_load:
        player_setup()


def load_room(room):
    global next_room, first_load

    clear_room()
    f = open("map_layout", "a")
    f.close()
    r = open("map_layout", "r")
    data = r.readlines()
    if data:
        for line in data:
            pieces = line.split(":")
            if int(pieces[0]) == room:
                # Convert tile data to tiles
                data = data[data.index(line)]
                data = data.split(":")
                t_data = data[1].split("#")
                for tile_data in t_data:
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
                        if first_load:
                            plr.pos.x = x
                            plr.pos.y = y
                # Apply room stats
                room_stats = data[2].split("/")
                for i in range(len(room_stats)):
                    next_room[i] = int(room_stats[i])
    plr.ground_tiles = ground_tiles
    plr.water_tiles = water_tiles
    first_load = False


def transition_load(room, direction):
    global next_room, first_load

    f = open("map_layout", "a")
    f.close()
    r = open("map_layout", "r")
    data = r.readlines()
    if data:
        for line in data:
            pieces = line.split(":")
            if int(pieces[0]) == room:
                # Convert tile data to tiles
                data = data[data.index(line)]
                data = data.split(":")
                t_data = data[1].split("#")
                for tile_data in t_data:
                    values = tile_data.split("&")
                    if "\n" in values[1]:
                        values[1] = values[1][:1]
                    position = values[0].split("/")
                    x = int(position[0])
                    y = int(position[1])
                    if direction == 0:
                        all_tiles.append((pygame.Rect(x, y - HEIGHT, 20, 20), values[1]))
                    elif direction == 1:
                        all_tiles.append((pygame.Rect(x, y + HEIGHT, 20, 20), values[1]))
                    elif direction == 2:
                        all_tiles.append((pygame.Rect(x - WIDTH, y, 20, 20), values[1]))
                    elif direction == 3:
                        all_tiles.append((pygame.Rect(x + WIDTH, y, 20, 20), values[1]))
                    version = int(values[1])
                    if version == 0:
                        # Ground tile
                        ground_tiles.append(pygame.Rect(x + WIDTH, y, 20, 20))
                    elif version == 1:
                        # Water tile
                        water_tiles.append(pygame.Rect(x + WIDTH, y, 20, 20))
                    elif version == 2:
                        # Player spawn point
                        player_spawn_point.x = x
                        player_spawn_point.y = y
                        if first_load:
                            plr.pos.x = x
                            plr.pos.y = y
                # Apply room stats
                room_stats = data[2].split("/")
                for i in range(len(room_stats)):
                    next_room[i] = int(room_stats[i])


if autoload:
    load_room(room)


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


def room_transition(direction):
    # Up down left right = 0 1 2 3
    # transition_speed = 5
    size = 0
    if direction == 0 or direction == 1:
        size = HEIGHT
    elif direction == 2 or direction == 3:
        size = WIDTH
    smooth = 0
    distance = 0
    while distance < size:  # for i in range(300):#int(round(size / transition_speed))):
        screen.fill(screen_color)
        for tile in all_tiles:
            if direction == 0:
                tile[0].y += smooth
            elif direction == 1:
                tile[0].y -= smooth
            elif direction == 2:
                tile[0].x += smooth
            elif direction == 3:
                tile[0].x -= smooth
            pygame.draw.rect(screen, (100, 100, 100), tile[0])
            pygame.draw.rect(screen, (255, 100, 100), [plr.pos.x - 20, plr.pos.y - 20, 20, 20])
        if direction == 0:
            plr.pos.y += smooth
        elif direction == 1:
            plr.pos.y -= smooth
        elif direction == 2:
            plr.pos.x += smooth
        elif direction == 3:
            plr.pos.x -= smooth
        distance += smooth
        if smooth < 10:
            smooth += 0.05
        plr.time_since_last_dash += 999
        plr.can_dash = True
        pygame.display.update()


def draw_tiles():
    for tile in ground_tiles:
        pygame.draw.rect(screen, (100, 100, 100), tile)


""" NORMAL RUNTIME BEHAVIOUR """
while not edit_mode:
    screen.fill(screen_color)
    draw_water()
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            quit()

    plr.update()

    if plr.pos.x > WIDTH + 15:
        room = next_room[3]
        transition_load(room, 3)
        room_transition(3)
        load_room(room)
    if plr.pos.x < 0 + 5:
        room = next_room[2]
        transition_load(room, 2)
        room_transition(2)
        load_room(room)
    if plr.pos.y < 0 - 5:
        room = next_room[0]
        transition_load(room, 0)
        room_transition(0)
        load_room(room)
    if plr.pos.y > HEIGHT:
        room = next_room[1]
        transition_load(room, 1)
        room_transition(1)
        load_room(room)

    draw_tiles()

    pygame.display.update()

    clock.tick(60)

""" EDIT MODE """


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

    # Add player spawn point
    room_save_code += str(int(player_spawn_point.x)) + "/" + str(int(player_spawn_point.y)) + "&2#"

    # Remove the hashtag from the end of the room code section
    room_save_code = room_save_code[:-1]

    room_stats_data = str(next_room[0]) + "/" + str(next_room[1]) + "/" + str(next_room[2]) + "/" + str(next_room[3])

    room_save_code += ":" + room_stats_data

    return room_save_code


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


def save_layout():
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


# Draw all tiles
def draw_all_tiles():
    for tile in ground_tiles:
        pygame.draw.rect(screen, tile_color, tile)
    for tile in water_tiles:
        pygame.draw.rect(screen, water_color, tile)


def edit_level_stats():
    choice = input("1. Set Room Transitions\n")
    if choice == "1":
        side = int(input("1. Up\n2. Down\n3. Left\n4. Right\n"))
        the_room = int(input("Which room should it transition to?\n"))
        next_room[side - 1] = the_room
        print("Successfully changed it!")


# Loop for when editing
while edit_mode:
    screen.fill(screen_color)
    draw_water()
    pygame.draw.rect(screen, (255, 100, 100), [player_spawn_point.x, player_spawn_point.y, 20, 20])
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            # Save the current room before closing
            save_layout()
            quit()

    # Edit mode GUI
    edit_buttons()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_e]:
        edit_level_stats()

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

    # Draw all the tiles
    draw_all_tiles()

    pygame.display.update()
