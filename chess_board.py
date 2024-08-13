import pygame, json
from globals import BLACK, WHITE, YELLOW, BLUE, RED, TILES_IN_ROW, draw_opaque_rect
from chess_tile import Tile
import chess_piece

class Board:
    def __init__(self, screen, height, width, x, y):
        self.screen = screen
        # The mask layer allows me to draw things that can't be drawn over with tiles or pieces
        self.mask_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        # self.mask_layer.set_alpha(128)
        
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

        # Contains a dictionary with a coordinate of a piece as the key
        # the value is each possible move that piece could make
        self.possible_moves_dict = {}

    def init_locations_dict(self, json_path):
        f = open(json_path)
        self.pieces_locations_dict = json.load(f)
        f.close()
        
    # Calculates the width and height of each of the tiles
    def init_tiles(self):
        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                # If height + width is even, tile is white, else it's black
                color = WHITE if ((row + col) % 2) == 0 else BLACK

                self.tiles[row][col] = Tile(self.tile_width, self.tile_height, col, row, color)
                tile = self.tiles[row][col]

                coords = f"{col}, {row}"
                if coords in self.pieces_locations_dict:
                    piece_val = self.pieces_locations_dict[coords]
                    PieceType = chess_piece.Piece.make_piece(piece_val[1]) # index 3 is the location of the piece char
                    if PieceType:
                        tile.piece = PieceType(piece_val[0], col, row, self.tile_width, self.tile_height)

    def draw_possible_moves(self, moves):
        if moves == None: return
        for tile in moves:
            # Uses mask layer instead so that tile drawing doesn't draw over the move display
            draw_opaque_rect(self.mask_layer, tile, BLUE, 128)

    def draw_board(self):
        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = self.tiles[row][col]

                self.draw_tile(tile)
                if tile.piece and not tile.piece.being_dragged:
                    piece_img = tile.piece.img
                    self.screen.blit(piece_img, (tile.x, tile.y))

                if self.mouse_pos == (col, row):
                    # Draws a yellow border around the tile your mouse is currently over
                    pygame.draw.rect(self.mask_layer, YELLOW, (tile.x, tile.y, self.tile_width, self.tile_width), 5)

                    # Draw possible moves
                    piece_moves = self.possible_moves_dict.get((col, row))
                    if piece_moves != None and not tile.piece.being_dragged:
                        self.draw_possible_moves(piece_moves)

    def draw_tile(self, tile):
        pygame.draw.rect(self.screen, tile.color, tile)
    
    # Converts the mouse pos to a coord on the board
    def set_mouse_rel(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        x = int((mouse_x - self.x) / self.tile_width)
        y = int((mouse_y - self.y) / self.tile_height)
        self.mouse_pos = (x, y)
        # print(f"Mouse pos is: {self.mouse_pos}")
        return (x, y)
    
    def mouse_over_tile(self, x, y):
        self.tiles[x][y]

    def set_possible_moves(self):
        tiles = self.tiles
        moves = {}

        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = tiles[row][col]
                piece = tile.piece
                if piece and piece.color:
                    piece_moves = piece.get_moves(self)
                    if piece_moves != None:
                        moves[(col, row)] = piece_moves
                # else:
                #     # For debugging if tiles can be moved to
                #     pygame.draw.rect(self.mask_layer, RED, (tile.x, tile.y, self.tile_width, self.tile_width))

        self.possible_moves_dict = moves