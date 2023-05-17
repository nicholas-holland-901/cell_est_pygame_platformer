import os
import pygame

# Import images
title = pygame.transform.scale(pygame.image.load(os.path.join("title_screen.png")), (960, 540))

class Menu:

    def __init__(self, font):
        self.visible = True
        self.font = font
        self.button_light = pygame.transform.scale(pygame.image.load(os.path.join("button_background_light.png")), (216, 50))
        self.button_dark = pygame.transform.scale(pygame.image.load(os.path.join("button_background_dark.png")), (216, 50))

    def Enable(self):
        self.visible = True

    def Disable(self):
        self.visible = False

    def CheckButton(self, rect):
        # Check if mouse is on top of a button's rect
        if rect[0] < pygame.mouse.get_pos()[0] < rect[0] + rect[2] and rect[1] < pygame.mouse.get_pos()[1] < rect[1] + rect[3]:
            return True

    def CheckPress(self):
        if self.CheckButton([360, 290, 216, 50]):
            # Play button clicked
            return True
        elif self.CheckButton([360, 390, 216, 50]):
            # Exit button clicked
            quit()
        return False

    def Draw(self, window):
        # Draw the main menu
        window.blit(title, (0, 0))
        # Determine if mouse is on button, and if it is, draw the darker button
        if self.CheckButton([360, 290, 216, 50]):
            window.blit(self.button_dark, (360, 290))
        else:
            window.blit(self.button_light, (360, 290))
        if self.CheckButton([360, 390, 216, 50]):
            window.blit(self.button_dark, (360, 390))
        else:
            window.blit(self.button_light, (360, 390))
        # Draw the text on the screen
        window.blit(self.font.render("Play", True, "white"), (440, 295))
        window.blit(self.font.render("Exit", True, "white"), (440, 395))
