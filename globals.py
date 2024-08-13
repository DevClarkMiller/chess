import pygame, os
from enum import Enum

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (252, 186, 3)
BLUE = (3, 127, 252)
RED = (235, 64, 52)
TILES_IN_ROW = 8

imgs_dict = {}

def init_pieces_icons(dir):
    for file in os.scandir(dir):
        # Get full path of file
        if file.is_file():
            imgs_dict[file.name] = file.path
            
def draw_opaque_rect(screen, rect, color, alpha):
    # Create a surface with per-pixel alpha transparency
    s = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    # Fill the surface with the color and desired alpha value
    s.fill((*color, alpha))
    # Blit this surface onto the destination surface (which could be the mask layer)
    screen.blit(s, (rect.x, rect.y))
 

# The value for each of the pieces
class Piece_Values(Enum):
    Pawn = 1
    Knight = 3
    Bishop = 3
    Rook = 5
    Queen = 9
