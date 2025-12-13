# cell_est_pygame_platformer
Platformer I made in high school using PyGame!!

<img width="956" height="538" alt="pygame_image_1" src="https://github.com/user-attachments/assets/9a362da3-5c97-4efb-b182-8e48dab04c04" />

Player can move left/right, jump, walljump, and dash upwards to navigate 11 levels containing ground, hazards, and water.

<img width="957" height="587" alt="pygame_image_3" src="https://github.com/user-attachments/assets/13e4a35a-7078-4a01-91eb-2802a557e84a" />

Levels were created using custom level editor. Setting boolean "edit_mode" to True inside main.py changes game to level editor upon launch. Levels are drawn on a grid using a selection of different tile types selected from a menu on the bottom of the screen. The level is then saved as an array into text file map_layout, including its directional positioning relative to other levels, so the screen can smoothly transition/slide over properly.

<img width="958" height="540" alt="pygame_image_2" src="https://github.com/user-attachments/assets/1cdfb0f9-e829-4ad5-812d-662b64c889f7" />
