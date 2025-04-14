import pygame
import traceback

import shared

colours = shared.colours

class Button:
    buttons = []
    def __init__(
            self, 
            text, 
            window, 
            buttonfont, 
            x=0, y=0, 
            width=100, height=20, 
            textcolour=colours["black"], 
            buttoncolour=colours["grey"], 
            padding=4, 
            function=None, args=None
        ):
        
        Button.buttons.append(self)
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.window = window
        self.buttonfont = buttonfont
        self.textcolour = textcolour
        self.defaulttextcolour = textcolour
        self.buttoncolour = buttoncolour
        self.defaultbuttoncolour = buttoncolour
        self.padding = padding
        self.function = function
        self.args = args
        self.buttonrect = pygame.Rect(self.x, self.y, self.width, self.height)  # create a rectangle for the button
        self.timesclicked = 0
        if function is None:            # if no function is provided
            Button.buttons.remove(self) # delete the button 

    def render(self):
        pygame.draw.rect(self.window, self.buttoncolour, self.buttonrect)   # draw the button's rectangle
        textsurf = self.buttonfont.render(self.text, True, self.textcolour) # render the text to surface
        textrect = textsurf.get_rect()                                      # get the rectangle of the text surface                
        textrect.center = (self.x + self.width/2, self.y + self.height/2)   # center the text rectangle in the button rectangle
        self.window.blit(textsurf, textrect)                                # blit the text surface to the window

    def click(self):
        self.timesclicked += 1
        try:
            self.function(*([self.args]))
        except Exception as e:
            print(f"error when button {self.text} was clicked: {e}")
            traceback.print_exc()

    def tick(self, mousepos, clicking=False):
        mouse_x, mouse_y = mousepos
        if self.buttonrect.collidepoint(mouse_x, mouse_y):
            self.buttoncolour = colours["white"]
            self.textcolour = colours["black"]
            if clicking and self.function:
                self.click()
        else:
            self.buttoncolour = self.defaultbuttoncolour
            self.textcolour = self.defaulttextcolour

