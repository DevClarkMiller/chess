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

        # Save the location of the kings coords so that when needed to see if they're in check, don't have to iterate tiles to find each location
        self.whiteKingCoords = None
        self.blackKingCoords = None

    def in_check_after_move(self, move_og, move_dest, color):
        tile_og = self.tiles[move_og[1]][move_og[0]]
        tile_dest = self.tiles[move_dest[1]][move_dest[0]]

        piece_og = tile_og.piece
        piece_dest = tile_dest.piece

        king_coords = None

        if piece_og.piece_c == "k":
            if color == "b":
                king_coords = self.blackKingCoords
            else:
                king_coords = self.whiteKingCoords

        # Move piece over from og tile to dest tile
        chess_piece.Piece.move(tile_og, tile_dest)

        if piece_og.piece_c == "k":
            if color == "b":
                self.blackKingCoords = (tile_dest.piece.x, tile_dest.piece.y)
            else:
                self.whiteKingCoords = (tile_dest.piece.x, tile_dest.piece.y)

        # See if in check now that the piece has been moved
        in_check = self.in_check(color)

        # Restore the kings coordinates
        if piece_og.piece_c == "k":
            if color == "b":
                self.blackKingCoords = king_coords
            else:
                self.whiteKingCoords = king_coords

        # Restore piece positions
        tile_og.piece = piece_og
        tile_dest.piece = piece_dest
        chess_piece.Piece.move()
        tile_og.piece.set_coords(tile_og.tile_x, tile_og.tile_y)

        return in_check

    # Fn: in_check()
    # Brief: Checks the kings locations to see if there's any way they are in check
    # Params: - color: The color of the players king that needs to be checked
    # Return: Boolean if active players king is in check
    def in_check(self, color):
        king_coords = self.blackKingCoords if color == "b" else self.whiteKingCoords
        enemy_color = "w" if color == "b" else "b"
        enemy_moves = self.get_possible_moves(enemy_color, check_check=False)

        for move_from in enemy_moves: # Iterate over each of the possible moves in the dict
            for move_to in enemy_moves[move_from]:
                # print(f"MOVE TO {move_to} | KING COORDS {king_coords}")
                if move_to == king_coords:
                    print(f"{self.tiles[king_coords[1]][king_coords[0]]} KING IS IN CHECK")
                    return True

        return False
    
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

    # Fn: next_turn()
    # Brief: Transitions the active player to the opposite color
    def next_turn(self):
        self.active_player = "w" if self.active_player == "b" else "b"

    # Fn: copy()
    # Brief: Copies each of the members from the board, this also copies each tile and the pieces in those tiles,
    # the purpose of this function is for the minimax for checking board possabilities without mutating the in play board
    # Return: Copy of the entire board
    def copy(self):
        copy = Board(self.screen, self.height, self.width, self.x, self.y)

        copy.active_player = self.active_player
        copy.white_score = self.white_score
        copy.black_score = self.black_score
        copy.game_over = self.game_over
        copy.mouse_pos = self.mouse_pos
        copy.pieces_locations_dict = self.pieces_locations_dict
        copy.past_moves = self.past_moves
        copy.blackKingCoords = self.blackKingCoords
        copy.whiteKingCoords = self.whiteKingCoords

        # Iterate over the tiles of the board and create a copy if there's a piece present
        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                copy.tiles[row][col] = self.tiles[row][col].copy()

        return copy
    
    # Fn: print_game()
    # Brief: Prints out details of the current game
    def print_game(self):
        print(f"SCORE: WHITE - {self.white_score} | BLACK - {self.black_score}")
        print(f"PLAYER: {"WHITE" if self.active_player == "w" else "BLACK"}")

    def print_details(self):
        print(f"ACTIVE PLAYER: {self.active_player}")
        print(f"BLACK KING COORDS: {self.blackKingCoords}")
        print(f"WHITE KING COORDS: {self.whiteKingCoords}")

    # Fn: player_move()
    # Brief: Determines if a move is possible to the player based off the boards possible_moves_dict, if so
    # it will call the make_move func and go forward with the move
    # Params: - move: A tuple containing the move from and move to coordinates
    # Return: Boolean determining if the move isn't possible or if the move went through successfully
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

    # Fn: make_move()
    # Brief: Moves a piece from one tile to another, which can defeat a piece in the process
    # also saves the game state and appends it to the member property "past_moves" so that the 
    # move can be unmade very easily
    # Params: - Move: Tuple containing the move from and move to coordinates
    # Return: Boolean if the move was successful
    def make_move(self, move):
        move_from, move_to = move

        og_tile = self.tiles[move_from[1]][move_from[0]]
        dest_tile = self.tiles[move_to[1]][move_to[0]]

        previous_state = {
            "black_score": self.black_score,
            "white_score": self.white_score,
            "tile1": og_tile.copy(),
            "tile2": dest_tile.copy(),
            "game_over": self.game_over,
            "whiteKingCoords": self.whiteKingCoords,
            "blackKingCoords": self.blackKingCoords
        }
        self.past_moves.append(previous_state)
        
        if dest_tile.piece:
            if self.active_player == "w":
                self.black_score -= piece_values[dest_tile.piece.piece_c]
            else:
                self.white_score -= piece_values[dest_tile.piece.piece_c]

        if og_tile.piece:
            og_color = og_tile.piece.color

            # Set the current piece on the new tile and/or morphs into a queen if possible
            if og_tile.piece.piece_c == "p" and (dest_tile.tile_y == 0 or dest_tile.tile_y == 7):
                self.tiles[move_from[1]][move_from[0]].piece = chess_piece.Queen(og_color, move_to[0], move_to[1], self.tile_width, self.tile_height)
                self.tiles[move_from[1]][move_from[0]].piece.set_image()
                # Then adjust the points since a queen has been added
                if self.active_player == "w":
                    self.white_score += piece_values["q"]
                else:
                    self.black_score += piece_values["q"]

            if move_from == self.blackKingCoords:
                self.blackKingCoords = move_to
            elif move_from == self.whiteKingCoords:
                self.whiteKingCoords = move_to

            chess_piece.Piece.move(og_tile, dest_tile)
            return True
        return False

    # Fn: unmake_move()
    # Brief: Pops the last element from the past_moves member and uses that to revert to the previous game state
    # this function is used mainly in the minimax algorithm
    def unmake_move(self):
        last_state = self.past_moves.pop()   # Pops the last index of the past moves so that it can be undone

        self.black_score = last_state["black_score"]
        self.white_score = last_state["white_score"]
        self.game_over = last_state["game_over"]

        tile1 = last_state["tile1"]
        tile2 = last_state["tile2"]

        self.whiteKingCoords = last_state["whiteKingCoords"]
        self.blackKingCoords = last_state["blackKingCoords"]

        self.tiles[tile1.tile_y][tile1.tile_x] = tile1
        self.tiles[tile2.tile_y][tile2.tile_x] = tile2

        self.next_turn()

    # Fn: check_game_over()
    # Brief: Sets the game_over member to true if a players score goes below the threshold
    # Return: Boolean if the game is over
    def check_game_over(self):
        if self.white_score <= 390 or self.black_score <= 390:
            return True
        return False
        
    # Fn: coord_in_board()
    # Brief: Checks if the coordinate is within the range of the board
    # Params: - Coord: Coordinate that could possibly be on the board
    # Return: Boolean if the coord is on the board
    @staticmethod
    def coord_in_board(coord):
        x, y = coord
        return (0 <= x < TILES_IN_ROW) and (0 <= y < TILES_IN_ROW)    

    # Fn: init_locations_dict()
    # Brief: Scans through a json file to position the pieces correctly, then assigns the locations to a dictionary
    # Params: - json_path: The path to the json file containing the locations of the pieces
    def init_locations_dict(self, json_path):
        f = open(json_path)
        self.pieces_locations_dict = json.load(f)
        f.close()
        
    # Fn: init_tiles()
    # Brief: Iterates the tiles member to provide each index with a tile, 
    # and if that tile contains a piece in the pieces_location_dict, it will provide it with
    # a piece as well
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

                        if PieceType == chess_piece.King:
                            if piece_val[0] == "b":
                                self.blackKingCoords = (col, row)
                            else:
                                self.whiteKingCoords = (col, row)

    # Fn: draw_possible_moves()
    # Brief: Takes in a list of possible moves, then draws a blue overlay on each of the spots so that the
    # player is aware of where they're able to move to
    # Params: - moves: A list of possible moves that a piece can move to
    def draw_possible_moves(self, moves):
        if moves == None: return
        for move in moves:
            # Uses mask layer instead so that tile drawing doesn't draw over the move display
            draw_opaque_rect(self.mask_layer, self.tiles[move[1]][move[0]], BLUE, 128)

    # Fn: check_mouse_hover()
    # Brief: Checks the players mouse positioning and if it's valid, it will draw a border around the tile 
    # to show what tile the player would select. If there are any valid moves for that tile if it contains a piece
    # it will display those too for the player as a visual aid
    def check_mouse_hover(self):
        x, y = self.mouse_pos
        if self.coord_in_board(self.mouse_pos):
            tile = self.tiles[y][x]
            if tile.piece and tile.piece.color != "w" or tile.piece == None or self.active_player != "w": return
            # Draws a yellow border around the tile your mouse is currently over
            pygame.draw.rect(self.mask_layer, YELLOW, (tile.x, tile.y, self.tile_width, self.tile_width), 5)

            # Draw possible moves
            piece_moves = self.possible_moves_dict.get((x, y))
            if piece_moves != None and not tile.piece.being_dragged:
                self.draw_possible_moves(piece_moves)

    # Fn: draw_tile()
    # Brief: A shorthand function for drawing a tile 
    # Params: - tile: A tile object
    def draw_tile(self, tile):
        pygame.draw.rect(self.screen, tile.color, tile)

    # Fn: draw_board()
    # Brief: Iterates over the board drawing each tile, and an image of the piece that's there
    # if there is a piece in that tile
    def draw_board(self):
        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = self.tiles[row][col]

                self.draw_tile(tile)
                if tile.piece and not tile.piece.being_dragged and tile.piece.img:
                    piece_img = tile.piece.img
                    self.screen.blit(piece_img, (tile.x, tile.y))

    # Fn: set_mouse_rel()
    # Brief: Calculates where the mouse pos lies in the context of the board tiles
    # Params: - mouse_pos: The raw mouse pos data obtained from pygame
    # Return: The relative mouse positioning
    def set_mouse_rel(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        x = int((mouse_x - self.x) / self.tile_width)
        y = int((mouse_y - self.y) / self.tile_height)
        self.mouse_pos = (x, y)
        # print(f"Mouse pos is: {self.mouse_pos}")
        return (x, y)

    # Fn: get_possible_moves()
    # Brief: Checks the possible moves of each of the pieces on the board and appends them to a dictionary with the from
    # location as the key and the value being a list of possible to locations
    # Return: The dictionary of possible moves on the board for the active player
    def get_possible_moves(self, color, check_check=True):
        king_in_check = False
        if check_check: 
            king_in_check = self.in_check(self.active_player)

        tiles = self.tiles
        moves = {}

        def get_moves(piece, col, row):
            piece_moves = piece.get_moves(self)
            if piece_moves != None:
                moves[(col, row)] = piece_moves

        if not king_in_check:
            for row in range(0, TILES_IN_ROW):
                for col in range(0, TILES_IN_ROW):
                    tile = tiles[row][col]

                    piece = tile.piece

                    if piece:
                        if piece.color == color:
                            get_moves(piece, col, row)       
                        
        else:   # Get the moves for the king that's in check
            # TODO - CHANGE TO GET MOVES FOR ANY PIECE THAT CAN PUT THE KING OUT OF CHECK
            x = 0
            y = 0
            if self.active_player == "w":
                x, y = self.whiteKingCoords
            else:
                x, y = self.blackKingCoords
            get_moves(tiles[y][x].piece, x, y)

        # Check over the moves to ensure it doesn't put the player in check
        if check_check:
            pass

        return moves