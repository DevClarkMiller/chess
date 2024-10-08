import pygame, json, random, colors
from globals import TILES_IN_ROW, draw_opaque_rect, piece_values, center_axis, central_tiles, Position_Values
from chess_tile import Tile
import chess_piece

class Board:
    def __init__(self, screen, height, width, x, y):
        self.screen = screen
        # The mask layer allows me to draw things that can't be drawn over with tiles or pieces
        self.mask_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
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
        
        self.game_over = None

        # Save the location of the kings coords so that when needed to see if they're in check, don't have to iterate tiles to find each location
        self.whiteKingCoords = None
        self.blackKingCoords = None

        self.active_tile = None

    def draw(self, layer, coords):
        self.screen.blit(layer, coords)

    def select_piece(self):
        rel_x, rel_y = self.mouse_pos
        if not Board.coord_in_board((rel_x, rel_y)): return
        if self.tiles[rel_y][rel_x]:    # Check if tile exists   
            tile = self.tiles[rel_y][rel_x]
            if tile.piece != None and tile.piece.color == "w" and tile.piece.color == self.active_player:
                # Resets the being dragged state of whatever piece was picked up
                if self.active_tile:
                    self.active_tile.piece.being_dragged = False

                self.active_tile = tile
                self.active_tile.piece.being_dragged = True

    def place_piece(self):
        rel_x, rel_y = self.mouse_pos
        self.active_tile.piece.being_dragged = False
        if Board.coord_in_board(self.mouse_pos): 
            # active_tile.piece.move(active_tile, board.tiles[rel_y][rel_x])
            from_coord = (self.active_tile.tile_x, self.active_tile.tile_y)
            if self.player_move((from_coord, (rel_x, rel_y))):
                self.possible_moves_dict = {} # Empty out the possible moves dict so that the moves can be determined again
                self.next_turn()
            self.active_tile = None

    def drag_piece(self, mouse_pos):
        if self.active_tile is None: return
        
        mouse_x, mouse_y = mouse_pos
        piece = self.active_tile.piece
        piece_img = piece.img

        # Centers the dragged tile to the middle of the mouse
        img_width, img_height = piece_img.get_size()
        
        centered_x = center_axis(mouse_x, img_width)
        centered_y = center_axis(mouse_y, img_height)

        self.draw(piece_img, (centered_x, centered_y))
        possible_moves = self.possible_moves_dict.get((piece.x, piece.y))
        self.draw_possible_moves(possible_moves)
    
    @staticmethod
    def print_moves(moves):
        print("------------------------------------------------------------------")
        for from_coord in moves:
            # Array of to moves from key
            print(f"[{from_coord[0]}, {from_coord[1]}]  -> ", end="")
            for to_coord in moves[from_coord]:
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
    
    # Fn: is_central_tile()
    # Brief: Evaluates if the tile is in the center squares, which is worth points for moving into as a player
    # Params: - tile: The tile that needs to be checked
    # Return: Boolean if the tile is a central tile
    def is_central_tile(self, tile):
        tile_coords = (tile.tile_x, tile.tile_y)
        return tile_coords in central_tiles
    
    # Fn: is_open_rank()
    # Brief: Useful for checking if the rooks or queens are in the open for positional point scoring
    # Params: - tile: The tile that needs to be checked
    # Return: Boolean if the tile is in an open rank
    def is_open_rank(self, tile):
        y = tile.tile_y

        # Check entire column to see if there's any pawns present, if not then then it's an open file
        for x in range(TILES_IN_ROW):
            if self.piece_at_coords((x, y)):
                if self.tiles[y][x].piece.piece_c == "p":
                    return False
        return True
    
    # Fn: is_open_file()
    # Brief: Useful for checking if the rooks or queens are in the open for positional point scoring
    # Params: - tile: The tile that needs to be checked
    # Return: Boolean if the tile is in an open file
    def is_open_file(self, tile):
        x = tile.tile_x

        # Check entire column to see if there's any pawns present, if not then then it's an open file
        for y in range(TILES_IN_ROW):
            if self.piece_at_coords((x, y)):
                if self.tiles[y][x].piece.piece_c == "p":
                    return False
        return True
    
    # Fn: on_seventh_rank()
    # Brief: Determines if a tile lies on the seventh rank
    def on_seventh_rank(self, tile):
        y = 1 if self.active_player == "w" else 6
        return tile.tile_y == y
    
    # Fn: update_scores()
    # Brief: Deducts the material score from the opposing player and grants the pos score to the active player
    # Params:   - material_score: 
    #           - pos_score: 
    def update_scores(self, material_score, pos_score):
        if self.active_player == "w":
            self.white_score += pos_score
            self.black_score -= material_score
        else:
            self.black_score += pos_score
            self.white_score -= material_score 
    
    # Fn: pawn_promotion_dist()
    # Brief: Returns the distance a pawn is from a promotion, this distance is used to scale the pawns value,
    # returns null if a promotion isn't possible if the pawn has no moves
    # Params:   - tile: The tile where the pawn will be
    def pawn_promotion_dist(self, tile):
        pass
    
    # Fn: get_move_penalties()
    # Brief: Gets the penalties a move gives, ie) taking back a move
    # Params    - og_tile: Tile that's being moved from
    #           - dest_tile: Tile that's being moved to
    def get_move_penalties(self, og_tile, dest_tile):
        material_score = 0
        pos_score = 0

        # Check to see if moving back into previous tile, deduct points if so
        prev_tile_1 = self.past_moves[-1]["tile1"]   # Gets last index in list
        og_piece = og_tile.piece
        prev_piece = prev_tile_1.piece
        if (prev_piece.piece_c == og_piece.piece_c) and (prev_piece.color == og_piece.color):
            og_piece_value = piece_values.get(og_piece.piece_c)
            pos_score -= (og_piece_value // 2) if og_piece_value is not None else 0
        
        self.update_scores(material_score, pos_score)

    # Fn: get_move_scores
    # Brief: Gets the positives from moving to a tile
    # Params    - og_tile: Tile that's being moved from
    #           - dest_tile: Tile that's being moved to
    def get_move_scores(self, og_tile, dest_tile):
        tile_is_central = self.is_central_tile(dest_tile)
        dest_has_piece = dest_tile.piece != None

        material_score = 0  # What's going to be removed from the opposing player
        pos_score = 0  # What's being granted to the active player

        og_piece_value = piece_values.get(og_tile.piece.piece_c)
        og_piece_value = 0 if og_piece_value == None else og_piece_value
        dest_piece_value = 0

        if dest_has_piece:
            dest_piece_value = piece_values.get(dest_tile.piece.piece_c)
             
            dest_piece_value = 0 if dest_piece_value == None else dest_piece_value

            # Check if the piece moving into the dest is worth less than the dest piece
            if og_piece_value < dest_piece_value:
                # Removes even more from material score to discourage sacrificing expensive pieces for small gains
                material_score -= (dest_piece_value - og_piece_value)   

            material_score -= dest_piece_value

        og_piece_rook_or_queen = og_tile.piece.piece_c == "q" or og_tile.piece.piece_c == "r"

        # Only award for moving into central tiles if the piece wasn't already in one
        if tile_is_central and not self.is_central_tile(og_tile):   
            pos_score += Position_Values.CentralControl.value

        if dest_has_piece and tile_is_central:
            material_score -= Position_Values.CentralControl.value
        
        # Only award for moving to an open file or rank if you weren't already in one
        if not self.is_open_file(og_tile) and self.is_open_file(dest_tile) and og_piece_rook_or_queen:
            pos_score += Position_Values.OpenFile.value
        if not self.is_open_rank(og_tile) and self.is_open_rank(dest_tile) and og_piece_rook_or_queen:
            pos_score += Position_Values.OpenRank.value

        if not self.on_seventh_rank(og_tile) and self.on_seventh_rank(dest_tile):
            pos_score += Position_Values.RookOnSvnth.value 

        # Check if the opponents piece is a queen and it's being lost early game which is under 10 total moves
        # If so, deduct even more points from the opposing player when they lose the queen
        # This is to discourage ai from rushing your king right away and losing its queen
        if dest_has_piece and dest_tile.piece.piece_c == "q" and len(self.past_moves) < 10:
            material_score -= og_piece_value

        self.update_scores(material_score, pos_score)

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

        self.get_move_scores(og_tile, dest_tile)
        self.get_move_penalties(og_tile, dest_tile)

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
        
        self.checkmate_stalemate() # Check if there's a checkmate or stalemate after this turn
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
    
    def piece_at_coords(self, coords):
        x, y = coords
        if self.tiles[y][x].piece:
            return True
        return False
    
    # Fn: checkmate_stalemate()
    # Brief: Checks the board to see if the game has ended by a checkmate or stalemate
    def checkmate_stalemate(self):
        legal_moves = 0
        for row in range(TILES_IN_ROW):
            for col in range(TILES_IN_ROW):
                tile = self.tiles[row][col]
                current_coord = (col, row)
                if self.piece_at_coords(current_coord) and tile.piece.color == self.active_player:
                    moves = tile.piece.get_moves(self)
                    for move in moves:
                        if not self.in_check_after_move(current_coord, move, self.active_player):
                            legal_moves +=1

        opponent = None
        if self.active_player == "w":
            opponent = "b"
        else:
            opponent = "w"

        if legal_moves == 0 and not self.in_check(self.active_player):
            self.game_over = ("Stalemate", None)
        elif legal_moves == 0:
            self.game_over = ("Checkmate", opponent)

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
                color = colors.WHITE if ((row + col) % 2) == 0 else colors.BLACK

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
        if moves == None or moves == False: return
        for move in moves:
            # Uses mask layer instead so that tile drawing doesn't draw over the move display
            draw_opaque_rect(self.mask_layer, self.tiles[move[1]][move[0]], colors.BLUE, 128)

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
            pygame.draw.rect(self.mask_layer, colors.YELLOW, (tile.x, tile.y, self.tile_width, self.tile_width), 5)

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
    
    # Fn: in_check()
    # Brief: Checks the kings locations to see if there's any way they are in check
    # Params: - color: The color of the players king that needs to be checked
    # Return: Boolean if active players king is in check
    def in_check(self, color):
        king_coords = self.blackKingCoords if color == "b" else self.whiteKingCoords

        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = self.tiles[row][col]
                piece_enemy = chess_piece.Piece.piece_is_enemy(tile, color)
                if piece_enemy:
                    moves = tile.piece.get_moves(self)
                    # if color == "w" and moves is not None:
                    #     print(moves)
                    if moves is None: continue
                    for move in moves:
                        if move[0] == king_coords[0] and move[1] == king_coords[1]:
                            return True

        return False
    
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
        tile_og.piece.set_coords((tile_og.tile_x, tile_og.tile_y))

        return in_check
    
    # Fn: randomize_moves()
    # Brief: Randomizes each array of to moves in the dictionary of possible moves
    # Params: = possible_moves: dictionary of possible moves
    def randomize_moves(self, possible_moves):
        for move_from in possible_moves:
            moves_to = possible_moves[move_from]
            random.shuffle(moves_to)

    # Fn: get_possible_moves()
    # Brief: Checks the possible moves of each of the pieces on the board and appends them to a dictionary with the from
    # location as the key and the value being a list of possible to locations
    # Return: The dictionary of possible moves on the board for the active player
    def get_possible_moves(self, color, rand_moves=False):
        moves = {}

        def get_moves(piece, col, row):
            piece_moves = piece.get_moves(self)
            if piece_moves != None:
                valid_moves = []
                for move in piece_moves:
                    if not self.in_check_after_move((col, row), move, color):
                        valid_moves.append(move)
                if valid_moves is not None and len(valid_moves) > 0:
                    moves[(col, row)] = valid_moves

        for row in range(0, TILES_IN_ROW):
            for col in range(0, TILES_IN_ROW):
                tile = self.tiles[row][col]
                piece = tile.piece
                if piece:
                    if piece.color == color:
                        get_moves(piece, col, row)       

        if rand_moves:  # Useful for the ai so that it doesn't just make the same moves every single game
            self.randomize_moves(moves)
        
        return moves