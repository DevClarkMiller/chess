import pygame
from globals import BLACK, WHITE

class Tile(pygame.Rect):    # Extends from rect for simple drawing with additional chess logic
    def __init__(self, width, height, x, y, color):
        # Set the values in the super based off calcs
        super(Tile, self).__init__((x * width, y * height, width, height))
        
        self.width = width
        self.height = height
        self.tile_x = x
        self.tile_y = y
        self.color = color
        self.piece = None

    def handle_mouse_over(self):
        print(f"Mouse if over tile at x: {self.tile_x}, y: {self.tile_y}")
        pass