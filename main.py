import os
import sys
from enum import Enum

import pygame

import player
import main_menu
import room_class
import room_editor_functions

autoload = True
edit_mode = False
all_tiles = []

# Load Images
gray_tile_img = pygame.transform.scale(pygame.image.load(os.path.join("gray_tile.png")), (20, 20))
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("background.png")), (960, 540))
win_ball_img = pygame.transform.scale(pygame.image.load(os.path.join("win_ball.png")), (150, 165))

if edit_mode:
    # Window dimensions
    WIDTH = 960
    HEIGHT = 590
else:
    # Window dimension
    WIDTH = 960
    HEIGHT = 540

pygame.init()
small_font = pygame.font.SysFont('Corbel', 35)

clock = pygame.time.Clock()

first_load = True

running = False

player_lives = 5

# Colors
tile_color = (100, 100, 100)
water_color = (75, 75, 255)

# Different types of tiles that can exist
class TileType(Enum):
    ground = 0
    water = 1
    plr_spawn_pos = 2
    spinners = 3


# The current room being drawn on the screen
current_room = room_class.Room(0)
room_number = 0

tile_type = TileType.ground

# Tile types
ground_tiles = []
water_tiles = []
change_tiles = []

# For the room transitions
next_room_tiles = []
next_room_water_tiles = []
next_room_spinners = []

# Window title
pygame.display.set_caption("Celeste")

# Background color
screen_color = (15, 15, 15)
default_player_color = (255, 100, 100)
no_dash_player_color = (100, 100, 255)

# Set window size
screen = pygame.display.set_mode((WIDTH, HEIGHT))

room_class.gray_tile_img = pygame.transform.scale(pygame.image.load(os.path.join("gray_tile.png")), (20, 20)).convert()

# Optimization
screen.set_alpha(None)
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
menu = main_menu.Menu(small_font)
tiles = [pygame.Rect(0, HEIGHT - 50, WIDTH, 50), pygame.Rect(500, 400, 30, 30), pygame.Rect(300, 400, 30, 70)]

def player_setup():
    global plr
    # Set all the collisions for the player (where all the stuff is in the level)
    plr = player.Player(screen, current_room.plr_spawn_point.x, current_room.plr_spawn_point.y)
    plr.ground_tiles = ground_tiles
    plr.water_tiles = water_tiles
    plr.spinners = current_room.spinners

plr = player.Player(screen, 0, 0)
player_setup()
end_screen = False

while not running:
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if menu.CheckPress():
                running = True
    menu.Draw(screen)
    pygame.display.update()


def clear_room():
    global ground_tiles, water_tiles, all_tiles, first_load
    global next_room_tiles, next_room_water_tiles, next_room_spinners

    # Reset all data regarding where tiles are
    ground_tiles = []
    water_tiles = []
    all_tiles = []
    next_room_tiles = []
    next_room_water_tiles = []
    next_room_spinners = []
    if first_load:
        player_setup()


def load_room(room):
    global next_room, first_load, current_room

    # Read the 'map_layout' text file to load a level
    clear_room()
    current_room = room_class.Room(room)
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
                    version = int(values[1])
                    if version == 0:
                        # Ground tile
                        current_room.ground_tiles.append(pygame.Rect(x, y, 20, 20))
                    elif version == 1:
                        # Water tile
                        current_room.water_tiles.append(pygame.Rect(x, y, 20, 20))
                    elif version == 2:
                        # Player spawn point
                        current_room.plr_spawn_point.x = x
                        current_room.plr_spawn_point.y = y
                        if first_load:
                            plr.pos.x = x + 20
                            plr.pos.y = y + 20
                    elif version == 3:
                        # Spinner tile
                        current_room.spinners.append(pygame.Rect(x, y, 20, 20))
                # Apply room stats
                room_stats = data[2].split("/")
                for i in range(len(room_stats)):
                    current_room.next_rooms[i] = int(room_stats[i])
    plr.ground_tiles = current_room.ground_tiles
    plr.water_tiles = current_room.water_tiles
    first_load = False
    current_room.generate_room_image()

def transition_load(room, direction):
    global next_room, first_load, current_room, next_room_tiles, next_room_water_tiles, next_room_spinners

    # Read the 'map_layout' text file to load a level
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
                        next_room_tiles.append(pygame.Rect(x, y, 20, 20))
                    elif version == 1:
                        # Water tile
                        next_room_water_tiles.append(pygame.Rect(x, y, 20, 20))
                    elif version == 2:
                        # Player spawn point
                        current_room.plr_spawn_point.x = x
                        current_room.plr_spawn_point.y = y
                        if first_load:
                            plr.pos.x = x
                            plr.pos.y = y
                    elif version == 3:
                        next_room_spinners.append(pygame.Rect(x, y, 20, 20))
                # Apply room stats
                room_stats = data[2].split("/")
                for i in range(len(room_stats)):
                    current_room.next_rooms[i] = int(room_stats[i])


if autoload:
    load_room(room_number)


# Used for buttons to see if the mouse cursor is in the rect
def in_region(rectangle, pos):
    if rectangle.x < pos[0] < rectangle.right and rectangle.y < pos[1] < rectangle.bottom:
        return True
    else:
        return False


def room_transition(direction):
    global next_room_tiles, player_lives
    # Up down left right = 0 1 2 3
    # transition_speed = 5
    first_room = pygame.Surface((960, 540))
    second_room = pygame.Surface((960, 540))
    x, y = 0, 0
    # Add current room to new screen thing
    first_room.blit(bg_img, (0, 0))
    second_room.blit(bg_img, (0, 0))
    # Create new level images for current and next level and load both to make transition animation
    for tile in current_room.ground_tiles:
        first_room.blit(room_class.gray_tile_img, tile)
    for tile in current_room.water_tiles:
        first_room.blit(room_class.water_tile_img, tile)
    for spinner in current_room.spinners:
        first_room.blit(room_class.spinner_img, pygame.Vector2(spinner.x - 5, spinner.y - 5))
    for tile in next_room_tiles:
        second_room.blit(room_class.gray_tile_img, tile)
    for tile in next_room_water_tiles:
        second_room.blit(room_class.water_tile_img, tile)
    for spinner in next_room_spinners:
        second_room.blit(room_class.spinner_img, pygame.Vector2(spinner.x - 5, spinner.y - 5))
    size = 0
    if direction == 0 or direction == 1:
        size = HEIGHT
    elif direction == 2 or direction == 3:
        size = WIDTH
    smooth = 2
    distance = 0
    while distance < size:
        screen.fill(screen_color)
        if direction == 0:
            y += smooth
            screen.blit(second_room, (x, y - HEIGHT))
        elif direction == 1:
            y -= smooth
            screen.blit(second_room, (x, y + HEIGHT))
        elif direction == 2:
            x += smooth
            screen.blit(second_room, (x - WIDTH, y))
        elif direction == 3:
            x -= smooth
            screen.blit(second_room, (x + WIDTH, y))
        screen.blit(first_room, (x, y))
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
        if smooth < 6 and distance < size / 2:
            smooth += 0.05
        elif smooth > 2 and distance > size / 2:
            smooth -= 0.03
        plr.time_since_last_dash += 999
        plr.can_dash = True
        screen.blit(small_font.render("Lives:" + str(player_lives), True, "white"), (0, 0))
        pygame.display.update()

def draw_end_screen():
    global running, end_screen, player_lives
    # Once the game is over
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Restart the game
            reset_player()
            clear_room()
            load_room(0)
            reset_player()
            player_lives = 5
            end_screen = False
    screen.fill("black")
    if player_lives >= 0:
        screen.blit(small_font.render("You're done.", True, "white"), (250, 250))
    else:
        screen.blit(small_font.render("You're dead.", True, "white"), (250, 250))
    screen.blit(small_font.render("(click to play again.)", True, "white"), (350, 450))
    pygame.display.update()


def reset_player():
    global player_lives, end_screen
    # Reset player on death back to spawn pos
    player_lives -= 1
    player_setup()
    plr.ground_tiles = current_room.ground_tiles
    plr.water_tiles = current_room.water_tiles
    plr.spinners = current_room.spinners
    if player_lives < 0:
        end_screen = True


""" NORMAL RUNTIME BEHAVIOUR """
while not edit_mode and running:
    if not end_screen:
        # Draw the current room and stuff
        screen.fill(screen_color)
        current_room.draw(screen)

        for event in pygame.event.get():
            # Close window on click
            if event.type == pygame.QUIT:
                quit()

        for spinner in current_room.spinners:
            if pygame.Rect.colliderect(plr.plr_hitbox, spinner):
                # Kill player when touching a spinner
                reset_player()

        if current_room.room_number == 10:
            # Draw the final win ball in the final room and go to end screen on touch
            screen.blit(win_ball_img, (300, 200))
            screen.blit(small_font.render("I'm done. Touch the object.", True, "white"), (480, 300))
            if pygame.Rect.colliderect(plr.plr_hitbox, pygame.Rect([300, 200, win_ball_img.get_width(), win_ball_img.get_height()])):
                end_screen = True
        elif current_room.room_number == 0:
            # Draw tutorial text in the first level
            screen.blit(small_font.render("A W D, Space for dash up", True, "white"), (480, 60))


        plr.update(screen)

        # Check if player is off the screen
        if plr.pos.x > WIDTH + 15:
            # Right
            room = current_room.next_rooms[3]
            transition_load(room, 3)
            room_transition(3)
            load_room(room)
        elif plr.pos.x < 0 + 5:
            # Left
            room = current_room.next_rooms[2]
            transition_load(room, 2)
            room_transition(2)
            load_room(room)
        elif plr.pos.y < 0 - 5:
            # Up
            room = current_room.next_rooms[0]
            transition_load(room, 0)
            room_transition(0)
            load_room(room)
        elif plr.pos.y > HEIGHT:
            # Down
            if current_room.next_rooms[1] >= 0:
                room = current_room.next_rooms[1]
                transition_load(room, 1)
                room_transition(1)
                load_room(room)
            else:
                # Kill side
                print("Fell into a pit!")
                reset_player()

        # print(round(clock.get_fps()))
        if player_lives >= 0:
            screen.blit(small_font.render("Lives:" + str(player_lives), True, "white"), (0, 0))
        
        pygame.display.update()

        clock.tick(60)
    else:
        draw_end_screen()



""" EDIT MODE """
def edit_buttons():
    global tile_type
    # Draw background for button area
    pygame.draw.rect(screen, (50, 50, 50), [0, HEIGHT - 49, WIDTH, 49])

    # Draw border on the top of the button area
    pygame.draw.rect(screen, (255, 255, 255), [0, HEIGHT - 50, WIDTH, 1])

    # Buttons rects to control the level editor
    ground_tile_button = pygame.draw.rect(screen, (100, 100, 100), [10, HEIGHT - 40, 30, 30])
    water_tile_button = pygame.draw.rect(screen, water_color, [50, HEIGHT - 40, 30, 30])
    plr_spawn_point_button = pygame.draw.rect(screen, (255, 100, 100), [90, HEIGHT - 40, 30, 30])
    spinner_button = pygame.draw.rect(screen, (0, 0, 200), [130, HEIGHT - 40, 30, 30])

    mouse_press = pygame.mouse.get_pressed()
    if mouse_press[0]:
        mouse_pos = pygame.mouse.get_pos()
        if in_region(ground_tile_button, mouse_pos):
            # Change current tile type to ground
            tile_type = TileType.ground
        elif in_region(water_tile_button, mouse_pos):
            # Change current tile type to water
            tile_type = TileType.water
        elif in_region(plr_spawn_point_button, mouse_pos):
            # Change current tile type to player spawn point
            tile_type = TileType.plr_spawn_pos
        elif in_region(spinner_button, mouse_pos):
            # Change current tile type to spinners
            tile_type = TileType.spinners


def edit_level_stats():
    global current_room
    # Change what borders transition to which room
    choice = input("1. Set Room Transitions\n")
    if choice == "1":
        side = int(input("1. Up\n2. Down\n3. Left\n4. Right\n"))
        the_room = int(input("Which room should it transition to?\n"))
        current_room.next_rooms[side - 1] = the_room
        print("Successfully changed it!")


# Loop for when editing
while edit_mode:
    pygame.draw.rect(screen, (255, 100, 100), [current_room.plr_spawn_point.x, current_room.plr_spawn_point.y, 20, 20])
    for event in pygame.event.get():
        # Close window on click
        if event.type == pygame.QUIT:
            # Save the current room before closing
            room_editor_functions.save_layout(current_room)
            quit()

    # Edit mode GUI
    edit_buttons()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_e]:
        edit_level_stats()

    # Draw all the tiles
    current_room.generate_room_image()
    current_room.draw(screen)

    # Get mouse input, add/remove tiles
    mouse_press = pygame.mouse.get_pressed()
    if mouse_press[0] and pygame.mouse.get_pos()[1] < 540:
        # Place tile on left click
        mouse = room_editor_functions.round_to_tile(pygame.mouse.get_pos())
        tile_rect = pygame.Rect(mouse[0], mouse[1], 20, 20)
        if tile_type.value == 0 and tile_rect not in current_room.ground_tiles:
            # Place a ground tile
            current_room.ground_tiles.append(tile_rect)
        elif tile_type.value == 1 and tile_rect not in current_room.water_tiles:
            # Place a water tile
            current_room.water_tiles.append(tile_rect)
        elif tile_type.value == 2:
            # Place a player spawn point
            current_room.plr_spawn_point.x = tile_rect.x
            current_room.plr_spawn_point.y = tile_rect.y
        elif tile_type.value == 3 and tile_rect not in current_room.spinners:
            # Place a spinner
            current_room.spinners.append(tile_rect)
    if mouse_press[2] and pygame.mouse.get_pos()[1] < 540:
        # Delete tile on right click
        mouse = room_editor_functions.round_to_tile(pygame.mouse.get_pos())
        tile_rect = pygame.Rect(mouse[0], mouse[1], 20, 20)
        new_tile = (tile_rect, tile_type.value)
        if tile_rect in current_room.ground_tiles:
            # Delete the ground tile
            current_room.ground_tiles.remove(tile_rect)
        elif tile_rect in current_room.water_tiles:
            # Delete the water tile
            current_room.water_tiles.remove(tile_rect)
        elif tile_rect in current_room.spinners:
            # Delete the spinner tile
            current_room.spinners.remove(tile_rect)

    pygame.display.update()

