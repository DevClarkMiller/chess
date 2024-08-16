import pygame, json
from globals import BLACK, WHITE, YELLOW, BLUE, RED, TILES_IN_ROW, draw_opaque_rect, piece_values
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
        self.past_moves = []    # Contains a series of objects that store values about the game state, useful for minimax backtracking

        self.active_player = "w"    # White always goes first in chess
        self.white_score = 1290
        self.black_score = 1290
        
        self.game_over = False

    def print_moves(self, moves):
        print("------------------------------------------------------------------")
        for from_coord in moves:
            # Array of to moves from key
            print(f"[{from_coord[0]}, {from_coord[1]}]  -> ", end="")
            for to_coord in moves(from_coord):
                if to_coord:
                    print(f"[{to_coord[0]}, {to_coord[1]}], ", end="")
            print() # For newline
        print("------------------------------------------------------------------")

    def next_turn(self):
        self.active_player = "w" if self.active_player == "b" else "b"

    # Copies the board so that minimax won't modify the values
    def copy(self):
        copy = Board(self.screen, self.height, self.width, self.x, self.y)

        copy.active_player = self.active_player
        copy.white_score = self.white_score
        copy.black_score = self.black_score
        copy.game_over = self.game_over
        copy.mouse_pos = self.mouse_pos
        copy.pieces_locations_dict = self.pieces_locations_dict
        copy.past_moves = self.past_moves

        # Iterate over the tiles of the board and create a copy if there's a piece present
        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                copy.tiles[row][col] = self.tiles[row][col].copy()

        return copy
    
    def print_game(self):
        print(f"SCORE: WHITE - {self.white_score} | BLACK - {self.black_score}")
        print(f"PLAYER: {"WHITE" if self.active_player == "w" else "BLACK"}")

    def player_move(self, move):
        move_from, move_to = move

        move_possible = False
        # Check to see if move can be made given the current tiles coords
        possible_moves = self.possible_moves_dict.get(move_from)

        if possible_moves == None or len(possible_moves) == 0:
            return False

        for possible_move in possible_moves:
            if move_to == possible_move:
                move_possible = True
                break

        if not move_possible:
            return False
        
        return self.make_move(move)

    def make_move(self, move):
        move_from, move_to = move

        og_tile = self.tiles[move_from[1]][move_from[0]]
        dest_tile = self.tiles[move_to[1]][move_to[0]]

        previous_state = {
            "black_score": self.black_score,
            "white_score": self.white_score,
            "tile1": og_tile.copy(),
            "tile2": dest_tile.copy(),
            "game_over": self.game_over
        }
        self.past_moves.append(previous_state)
        
        if dest_tile.piece:
            if self.active_player == "w":
                self.black_score -= piece_values[dest_tile.piece.piece_c]
            else:
                self.white_score -= piece_values[dest_tile.piece.piece_c]

        if og_tile.piece:
            og_tile.piece.move(og_tile, dest_tile)

        return True

    # Undoes a previous move by reverting to a stored gamestate
    def unmake_move(self):
        last_state = self.past_moves.pop()   # Pops the last index of the past moves so that it can be undone

        self.black_score = last_state["black_score"]
        self.white_score = last_state["white_score"]
        self.game_over = last_state["game_over"]

        tile1 = last_state["tile1"]
        tile2 = last_state["tile2"]

        self.tiles[tile1.tile_y][tile1.tile_x] = tile1
        self.tiles[tile2.tile_y][tile2.tile_x] = tile2

        self.next_turn()

    # Only removing will result in a score <= 390
    def check_game_over(self):
        if self.white_score <= 390 or self.black_score <= 390:
            self.game_over = True

    def check_game_over(self):
        if self.white_score <= 390 or self.black_score <= 390:
            return True
        return False
        
    @staticmethod
    def coord_in_board(coord):
        x, y = coord
        return (0 <= x < TILES_IN_ROW) and (0 <= y < TILES_IN_ROW)    

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
                        tile.piece.set_image()

    def draw_possible_moves(self, moves):
        if moves == None: return
        for move in moves:
            # Uses mask layer instead so that tile drawing doesn't draw over the move display
            draw_opaque_rect(self.mask_layer, self.tiles[move[1]][move[0]], BLUE, 128)

    def check_mouse_hover(self):
        x, y = self.mouse_pos
        in_range = lambda pos: 0 <= pos < TILES_IN_ROW
        if in_range(x) and in_range(y):
            tile = self.tiles[y][x]
            if tile.piece and tile.piece.color != "w" or tile.piece == None or self.active_player != "w": return
            # Draws a yellow border around the tile your mouse is currently over
            pygame.draw.rect(self.mask_layer, YELLOW, (tile.x, tile.y, self.tile_width, self.tile_width), 5)

            # Draw possible moves
            piece_moves = self.possible_moves_dict.get((x, y))
            if piece_moves != None and not tile.piece.being_dragged:
                self.draw_possible_moves(piece_moves)

    def draw_board(self):
        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = self.tiles[row][col]

                self.draw_tile(tile)
                if tile.piece and not tile.piece.being_dragged and tile.piece.img:
                    piece_img = tile.piece.img
                    self.screen.blit(piece_img, (tile.x, tile.y))

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

    def get_possible_moves(self):
        tiles = self.tiles
        moves = {}

        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = tiles[row][col]

                piece = tile.piece
                if piece and piece.color == self.active_player:
                    piece_moves = piece.get_moves(self)
                    if piece_moves != None:
                        moves[(col, row)] = piece_moves

        num_moves = len(moves)

        # if num_moves > 0:
        #     print(f"NUM OF HARVESTED MOVES: {len(moves)}")
        # else:
        #     print("NO MOVES FOUND")
        return moves