import pygame, json
from globals import BLACK, WHITE, YELLOW, TILES_IN_ROW
from chess_tile import Tile
import chess_piece

class Board:
    def __init__(self, screen, height, width, x, y):
        self.screen = screen
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.tile_width = int(width / TILES_IN_ROW)
        self.tile_height = int(height / TILES_IN_ROW)
        self.tiles = [[None for _ in range(TILES_IN_ROW)] for _ in range(TILES_IN_ROW)]
        self.mouse_pos = (0, 0)

        # Loads json of initial chess pieces
        self.pieces_locations_dict = None

    def init_locations_dict(self, json_path):
        f = open(json_path)
        self.pieces_locations_dict = json.load(f)
        f.close()
        
    # Calculates the width and height of each of the tiles
    def init_tiles(self):
        for i in range(0, TILES_IN_ROW):
            for j in range(0, TILES_IN_ROW):
                # If height + width is even, tile is white, else it's black
                color = WHITE if ((i + j) % 2) == 0 else BLACK

                self.tiles[i][j] = Tile(self.tile_width, self.tile_height, i, j, color)
                tile = self.tiles[i][j]

                coords = f"{i}, {j}"
                if coords in self.pieces_locations_dict:
                    piece_val = self.pieces_locations_dict[coords]
                    PieceType = chess_piece.Piece.make_piece(piece_val[1]) # index 3 is the location of the piece char
                    if PieceType:
                        tile.piece = PieceType(piece_val[0], i, j, self.tile_width, self.tile_height )

    def draw_board(self):
        for i in range(0, TILES_IN_ROW):
            for j in range(0, TILES_IN_ROW):
                tile = self.tiles[i][j]
                if self.mouse_pos == (i, j):
                    tile.color = YELLOW
                else: 
                    tile.color = tile.og_color
                self.draw_tile(tile)
                if tile.piece:
                    piece_img = tile.piece.img
                    self.screen.blit(piece_img, (tile.x, tile.y))

    def draw_tile(self, tile):
        pygame.draw.rect(self.screen, tile.color, tile)
        pass
    
    # Converts the mouse pos to a coord on the board
    def mouse_pos_rel(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        x = int((mouse_x - self.x) / self.tile_width)
        y = int((mouse_y - self.y) / self.tile_height)
        self.mouse_pos = (x, y)
        # print(f"Mouse pos is: {self.mouse_pos}")
        return (x, y)
    
    def mouse_over_tile(self, x, y):
        self.tiles[x][y]