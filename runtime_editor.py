import pygame
import main


# Buttons to control the level editor
def edit_buttons():
    # Draw background for button area
    pygame.draw.rect(main.screen, (50, 50, 50), [0, main.HEIGHT - 49, main.WIDTH, 49])

    # Draw border on the top of the button area
    pygame.draw.rect(main.screen, (255, 255, 255), [0, main.HEIGHT - 50, main.WIDTH, 1])

    # Buttons
    ground_tile_button = pygame.draw.rect(main.screen, (100, 100, 100), [10, main.HEIGHT - 40, 30, 30])
    water_tile_button = pygame.draw.rect(main.screen, main.water_color, [50, main.HEIGHT - 40, 30, 30])
    plr_spawn_point_button = pygame.draw.rect(main.screen, (255, 100, 100), [90, main.HEIGHT - 40, 30, 30])
    change_tile_button = pygame.draw.rect(main.screen, (255, 255, 255), [130, main.HEIGHT - 40, 30, 30])

    level_change_button = pygame.draw.rect(main.screen, (255, 255, 255), [920, main.HEIGHT - 40, 30, 30])

    mouse_press = pygame.mouse.get_pressed()
    if mouse_press[0]:
        mouse_pos = pygame.mouse.get_pos()
        if main.in_region(ground_tile_button, mouse_pos):
            main.tile_type = main.TileType.ground
        elif main.in_region(water_tile_button, mouse_pos):
            main.tile_type = main.TileType.water
        elif main.in_region(plr_spawn_point_button, mouse_pos):
            main.tile_type = main.TileType.plr_spawn_pos
        elif main.in_region(level_change_button, mouse_pos):
            main.tile_type = main.TileType.room_transition


# Generate room code that can be used to load to level and save the layout
def generate_room_code():
    room_save_code = str(main.room) + ":"
    tile_code = ""
    # Add the ground tiles already in the room
    for tile in main.all_tiles:
        tile_code = str(tile[0].x) + "/" + str(tile[0].y) + "&" + str(tile[1]) + "#"
        room_save_code += tile_code
    # Draw player spawn point
    room_save_code += str(int(main.player_spawn_point.x)) + "/" + str(int(main.player_spawn_point.y)) + "&2#"

    # Remove the hashtag from the end of the room code
    room_save_code = room_save_code[:-1]

    file = open("map_layout", 'r')
    lines = file.readlines()

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
        if int(line[:1]) == main.room:
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
