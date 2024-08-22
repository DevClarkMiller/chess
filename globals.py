import pygame, os
from enum import Enum

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (252, 186, 3)
BLUE = (3, 127, 252)
RED = (235, 64, 52)
TILES_IN_ROW = 8
center_axis = lambda axis, measurment: axis - measurment // 2

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

central_tiles = [(3, 4), (4, 4), (3, 4), (4, 3)]

# The value for each of the pieces
piece_values = {
    "p": 10,
    "n": 30,
    "b": 30,
    "r": 50,
    "q": 90,
    "k": 900
}

class Position_Values(Enum):
    CentralControl = 1
    RookOpenTile = 2
    RookOnSvnth = 2
    OpenFile = 2
    OpenRank = 1