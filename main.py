import pygame
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

# Player stuff
plr_pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
plr_velocity = pygame.Vector2(0, 0)
direction = pygame.Vector2(0, 0)
plr_acceleration = pygame.Vector2(0, 0)
can_dash = True
grounded = False
dashing = False
jumping = False
in_water = False
trying_to_dash = False
dash_cooldown = 0
friction = -0.2
dash_power = 5
time_since_last_dash = 0
time_since_last_jump = 0
gravity_force = 0.4
gravity_acceleration = 0.7
dash_length = 400

player_spawn_point = pygame.Vector2(300, 400)

acceleration = 0.9

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
                        plr_pos.x = x
                        plr_pos.y = y


# Used for buttons to see if the mouse cursor is in the rect
def in_region(rectangle, pos):
    if rectangle.x < pos[0] < rectangle.right and rectangle.y < pos[1] < rectangle.bottom:
        return True
    else:
        return False


# Draw the player based on Vector2
def draw_player():
    # Draw player at Vector2 location
    if can_dash:
        pygame.draw.rect(screen, default_player_color, [plr_pos.x - 20, plr_pos.y - 20, 20, 20])
    else:
        pygame.draw.rect(screen, no_dash_player_color, [plr_pos.x - 20, plr_pos.y - 20, 20, 20])


# Get player input and move the player horizontally
def player_movement():
    # Global Vector2s
    global plr_velocity, plr_pos, plr_acceleration, direction
    # Global booleans
    global grounded, can_dash, dashing, jumping, trying_to_dash
    # Global ints/floats
    global time_since_last_jump, time_since_last_dash

    plr_acceleration = pygame.Vector2(0, 0)
    keys = pygame.key.get_pressed()

    direction = pygame.Vector2(0, 0)

    if keys[pygame.K_a]:
        plr_acceleration.x = -acceleration
    if keys[pygame.K_d]:
        plr_acceleration.x = acceleration

    if keys[pygame.K_w] and grounded:
        # Jump
        time_since_last_jump = pygame.time.get_ticks()
        jumping = True
        grounded = False
        plr_velocity.y = -6

    # Holding down jump makes it longer
    if keys[pygame.K_w] and not grounded and jumping and pygame.time.get_ticks() - time_since_last_jump < 200:
        plr_velocity.y = -6

    trying_to_dash = False

    if keys[pygame.K_LEFT]:
        trying_to_dash = True
        direction.x = 1
    if keys[pygame.K_RIGHT]:
        trying_to_dash = True
        direction.x = -1
    if keys[pygame.K_UP]:
        trying_to_dash = True
        direction.y = 1
    if keys[pygame.K_DOWN]:
        trying_to_dash = True
        direction.y = -1

    if trying_to_dash and can_dash:
        # Dash
        plr_velocity = pygame.Vector2(0, 0)
        dashing = True
        can_dash = False
        grounded = False
        time_since_last_dash = pygame.time.get_ticks()

    # Holding down dash makes it longer
    if trying_to_dash and not grounded and dashing and pygame.time.get_ticks() - time_since_last_dash < dash_length:
        plr_velocity.x = -dash_power * direction.x * 2
    else:
        dashing = False

    # Apply horizontal movement
    plr_acceleration.x += plr_velocity.x * friction
    plr_velocity += plr_acceleration
    plr_pos.x += plr_velocity.x + 0.5 * plr_acceleration.x


# Apply vertical gravity to the player character
def apply_player_gravity():
    global grounded
    global plr_acceleration
    global in_water
    global dashing
    global trying_to_dash

    # Apply gravity if not on the ground
    if not grounded and not dashing and not in_water:
        plr_velocity.y += gravity_force
        plr_pos.y += plr_velocity.y + gravity_acceleration * plr_acceleration.y
    elif grounded and not dashing and not in_water:
        plr_velocity.y = 0
        plr_acceleration.y = 0
    elif in_water and not dashing:
        plr_velocity.y -= gravity_force * 0.5
        plr_pos.y += plr_velocity.y + gravity_acceleration * plr_acceleration.y * 0.5

    # Holding down dash makes it longer
    if trying_to_dash and not grounded and dashing and pygame.time.get_ticks() - time_since_last_dash < dash_length:
        plr_velocity.y = -dash_power * direction.y
        plr_pos.y += plr_velocity.y
    else:
        dashing = False


# Draw the water tiles
def draw_water():
    for tile in water_tiles:
        pygame.draw.rect(screen, water_color, tile)


# Check for horizontal collision
def player_horizontal_collisions():
    global grounded
    global plr_pos
    global plr_acceleration
    global plr_velocity
    plr_hitbox = pygame.Rect(plr_pos.x - 20, plr_pos.y - 20, 20, 20)

    for tile in ground_tiles:
        pygame.draw.rect(screen, (100, 100, 100), tile)
        # Check horizontal collisions
        if pygame.Rect.colliderect(plr_hitbox, tile):
            if plr_velocity.x > 0:
                plr_velocity.x = 0
                plr_acceleration.x = 0
                plr_pos.x = tile.left
            if plr_velocity.x < 0:
                plr_acceleration.x = 0
                plr_velocity.x = 0
                plr_pos.x = tile.right + 20


# Check for vertical collision
def player_vertical_collisions():
    global grounded
    global plr_pos
    global plr_acceleration
    global plr_velocity
    plr_hitbox = pygame.Rect(plr_pos.x - 20, plr_pos.y - 20, 20, 20)

    for tile in ground_tiles:
        # Check vertical collisions
        if pygame.Rect.colliderect(plr_hitbox, tile):
            if plr_velocity.y > 0:
                grounded = True
                plr_acceleration.y = 0
                plr_velocity.y = 0
                plr_pos.y = tile.top
            if plr_velocity.y < 0:
                plr_velocity.y = 0
                plr_acceleration.y = 0
                plr_pos.y = tile.bottom + 20


# Check what state the player is in
def check_surroundings():
    global grounded
    global can_dash
    global in_water
    jump_hitbox = pygame.Rect(plr_pos.x - 20, plr_pos.y - 5, 20, 6)
    any_collide = False
    water_collide = False
    for tile in ground_tiles:
        if pygame.Rect.colliderect(jump_hitbox, tile):
            any_collide = True
    for piece in water_tiles:
        if pygame.Rect.colliderect(jump_hitbox, piece):
            water_collide = True
    if any_collide:
        grounded = True
        can_dash = True
    else:
        grounded = False
    if water_collide:
        in_water = True
    else:
        in_water = False
    if in_water:
        can_dash = True


# Normal runtime behaviour
while not edit_mode:
    screen.fill(screen_color)
    draw_water()
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            quit()

    # # Check if still dashing based on time
    # if time_since_last_dash != 0 and pygame.time.get_ticks() - time_since_last_dash >= dash_cooldown:
    #     dashing = False
    #     time_since_last_dash = 0

    player_movement()
    player_horizontal_collisions()
    apply_player_gravity()
    player_vertical_collisions()
    draw_player()
    check_surroundings()

    # pygame.display.update(plr_pos.x - 40, plr_pos.y - 40, 60, 60)
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
