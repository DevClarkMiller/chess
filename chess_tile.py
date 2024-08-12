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
        self.og_color = color
        self.color = color
        self.piece = None

    def handle_mouse_over(self):
        print(f"Mouse if over tile at x: {self.tile_x}, y: {self.tile_y}")
        pass

    def check_click(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        if mouse_x == self.tile_x and mouse_y == self.tile_y:
            # print(f"Mouse clicked at x: {self.tile_x} y: {self.tile_y}")
            if self.piece:
                pass
            
    # If you hold mouse down on tile to drag a piece
    def check_hold(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        if mouse_x == self.x and mouse_y == self.y:
            pass
        
