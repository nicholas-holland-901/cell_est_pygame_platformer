
# Generate room code that can be used to load to level and save the layout
def generate_room_code(current_room):
    room_save_code = str(current_room.room_number) + ":"
    # Add the ground tiles already in the room
    for tile in current_room.ground_tiles:
        tile_code = str(tile.x) + "/" + str(tile.y) + "&0#"
        room_save_code += tile_code
    for tile in current_room.water_tiles:
        tile_code = str(tile.x) + "/" + str(tile.y) + "&1#"
        room_save_code += tile_code
    for spinner in current_room.spinners:
        tile_code = str(spinner.x) + "/" + str(spinner.y) + "&3#"
        room_save_code += tile_code
    for spike in current_room.spikes:
        tile_code = str(spike.x) + "/" + str(spike.y) + "&4#"
        room_save_code += tile_code
    # Add player spawn point
    room_save_code += str(int(current_room.plr_spawn_point.x)) + "/" + str(int(current_room.plr_spawn_point.y)) + "&2#"
    # Remove the hashtag from the end of the room code section
    room_save_code = room_save_code[:-1]
    room_stats_data = str(current_room.next_rooms[0]) + "/" + str(current_room.next_rooms[1]) + "/" + str(current_room.next_rooms[2]) + "/" + str(current_room.next_rooms[3])
    room_save_code += ":" + room_stats_data
    return room_save_code

def save_layout(current_room):
    # Save the current room
    room_code = generate_room_code(current_room)
    file = open("map_layout", 'r')
    lines = file.readlines()
    w = open("map_layout", "w")
    exists = False
    for line in lines:
        if int(line[:1]) == current_room.room_number:
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
