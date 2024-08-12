import pygame, os
from enum import Enum

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (252, 186, 3)
TILES_IN_ROW = 8

imgs_dict = {}

def init_pieces_icons(dir):
    for file in os.scandir(dir):
        # Get full path of file
        if file.is_file():
            imgs_dict[file.name] = file.path
            

# The value for each of the pieces
class Piece_Values(Enum):
    Pawn = 1
    Knight = 3
    Bishop = 3
    Rook = 5
    Queen = 9
