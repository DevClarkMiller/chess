import pygame
from abc import ABC, abstractmethod
from globals import imgs_dict, TILES_IN_ROW

class Piece:
    def __init__(self, x, y, width, height, color, piece):
        self.color = color
        self.piece_c = piece
        self.img = None
        img_path = Piece.get_img_path(piece, color)
        if img_path:
            self.img = pygame.image.load(img_path)
            self.img = pygame.transform.scale(self.img, (width, height))

        self.value = 0

        # x and y are relative to the board
        self.x = x
        self.y = y

        # Just the width and height of the tiles
        self.width = width
        self.height = height

        self.being_dragged = False
        
        self.possible_moves = None
    
    def set_coords(self, coords):
        self.x, self.y = coords

    def piece_is_enemy(self, tile):
        return tile.piece and tile.piece.color != self.color
    
    def tile_available(self, tile):
        return tile.piece is None or (self.piece_is_enemy(tile))

    @staticmethod
    def make_piece(piece):
        if piece == "r": return Rook
        elif piece == "n": return Knight
        elif piece == "b": return Bishop
        elif piece == "k": return King
        elif piece == "q": return Queen
        elif piece == "p": return Pawn

    @staticmethod
    def get_img_path(piece, color):
        return imgs_dict[f"{piece}{color}.png"]
    
    # Checks the available moves this piece is able to go to, returns list of moves
    @abstractmethod
    def get_moves(self, board): pass

    # Moves the piece to the desired location if it's possible,
    # it knows if it's possible by checking if the potential move is
    # in the moves list 
    def move(self, og_tile, tile): 
        if self.possible_moves == None: return
        if og_tile == tile: return

        # Check each of the coords of the possible moves tiles 
        # to see if this move is available
        for possible_tile in self.possible_moves:
            if (tile.tile_x, tile.tile_y) == (possible_tile.tile_x, possible_tile.tile_y):
                tile.piece = self       # Set the current piece on the new tile
                tile.piece.set_coords((tile.tile_x, tile.tile_y))
                og_tile.piece = None    # Reset the tile you moved from
                return 

    # Gets the moves that a piece can make in a straight line
    def get_omni_moves(self, x_mod, y_mod, moves, tiles):
        x = self.x
        y = self.y
        num_moves = 0
        while True:
            can_move_x = 0 <= (x + x_mod) < TILES_IN_ROW
            can_move_y = 0 <= (y + y_mod) < TILES_IN_ROW

            # Allows alternate behavior based off the type of piece this is

            # Since pawns are the only piece that can't move backwards, just check to see which
            # color it is, then determine if the pawn is at it's start based off that
            pawn_at_start = self.piece_c == "p" and (
                (self.color == "w" and self.y == 6) or (self.color == "b" and self.y == 1))

            if self.piece_c == "k" and num_moves == 1:
                return
            elif self.piece_c == "p" and pawn_at_start and num_moves == 2:
                return 
            elif self.piece_c == "p" and not pawn_at_start and num_moves == 1:
                return 

            x += x_mod
            y += y_mod
            if can_move_x and can_move_y and self.tile_available(tiles[y][x]) or (self.piece_c == "p" and not tiles[y][x].piece):
                moves.append(tiles[y][x])
                num_moves +=1

                if self.piece_is_enemy(tiles[y][x]):
                    return
            else:
                return
            
    def get_all_dirs(self, moves, tiles):
        # 1. Get moves moving like rook
        self.get_omni_moves(-1, 0, moves, tiles)    # Left
        self.get_omni_moves(1, 0, moves, tiles)     # Right
        self.get_omni_moves(0, -1, moves, tiles)    # Up
        self.get_omni_moves(0, 1, moves, tiles)     # Down

        # 2. Get moves moving like bishop
        self.get_omni_moves(-1, -1, moves, tiles)   # Up left
        self.get_omni_moves(1, -1, moves, tiles)    # Up right
        self.get_omni_moves(-1, 1, moves, tiles)    # Down left
        self.get_omni_moves(1, 1, moves, tiles)     # Down right
        

class King(Piece):
    def __init__(self, color, x, y, width, height):
        super(King, self).__init__(x, y, width, height, color, "k")

    # get_all_dirs works differently if the piece is a king,
    # so implementation of get_moves is the same as the queens
    def get_moves(self, board):
        moves = []
        self.get_all_dirs(moves, board.tiles)
        self.possible_moves = moves if len(moves) > 0 else None
        return moves if len(moves) > 0 else None

class Queen(Piece):
    def __init__(self, color, x, y, width, height):
        super(Queen, self).__init__(x, y, width, height, color, "q")

    def get_moves(self, board):
        moves = []
        self.get_all_dirs(moves, board.tiles)
        self.possible_moves = moves if len(moves) > 0 else None
        return moves if len(moves) > 0 else None
        
class Bishop(Piece):
    def __init__(self, color, x, y, width, height):
        super(Bishop, self).__init__(x, y, width, height, color, "b")

    def get_moves(self, board):
        moves = []
        tiles = board.tiles

        # Get moves from moving diagonally
        self.get_omni_moves(-1, -1, moves, tiles)   # Up left
        self.get_omni_moves(1, -1, moves, tiles)    # Up right
        self.get_omni_moves(-1, 1, moves, tiles)    # Down left
        self.get_omni_moves(1, 1, moves, tiles)     # Down right
        self.possible_moves = moves if len(moves) > 0 else None
        return moves if len(moves) > 0 else None

class Knight(Piece):
    def __init__(self, color, x, y, width, height):
        super(Knight, self).__init__(x, y, width, height, color, "n")

    # Gets moves in an l shaped pattern
    def get_moves(self, board):
        moves = []

        def get_l_move(x_mod, y_mod):
            new_x = self.x + (1 * x_mod)
            new_y = self.y + (2 * y_mod)
            if (0 <= new_x < TILES_IN_ROW) and (0 <= new_y < TILES_IN_ROW):
                if self.tile_available(board.tiles[new_y][new_x]):
                    moves.append(board.tiles[new_y][new_x])

        get_l_move(-1, -1)  # Up left
        get_l_move(1, -1)   # Up right
        get_l_move(-1, 1)   # Down left
        get_l_move(1, 1)    # Down right
        self.possible_moves = moves if len(moves) > 0 else None
        return moves if len(moves) > 0 else None

class Rook(Piece):
    def __init__(self, color, x, y, width, height):
        super(Rook, self).__init__(x, y, width, height, color, "r")

    def get_moves(self, board):
        moves = []
        tiles = board.tiles

        # Get the moves from moving in straight lines
        self.get_omni_moves(-1, 0, moves, tiles)    # Left
        self.get_omni_moves(1, 0, moves, tiles)     # Right
        self.get_omni_moves(0, -1, moves, tiles)    # Up
        self.get_omni_moves(0, 1, moves, tiles)     # Down
        self.possible_moves = moves if len(moves) > 0 else None
        return moves if len(moves) > 0 else None

class Pawn(Piece):
    def __init__(self, color, x, y, width, height):
        super(Pawn, self).__init__(x, y, width, height, color, "p")

    def get_moves(self, board):
        # Checks only a few surrounding tiles for moves since the pawns moveset is very limited
        moves = []
        tiles = board.tiles

        # 1. Get how many moves you can make forward
        if self.color == "w":
            self.get_omni_moves(0, -1, moves, tiles)
        else:
            self.get_omni_moves(0, 1, moves, tiles)            

        # 2. Check both diagonals
        upper_diag_in_bound = lambda x : x >= 0 and x <= TILES_IN_ROW and self.y - 1 >= 0 and self.y - 1 <= TILES_IN_ROW
        
        if upper_diag_in_bound(self.x - 1) and self.piece_is_enemy(board.tiles[self.y - 1][self.x - 1]):
            moves.append(tiles[self.y - 1][self.x - 1])

        if upper_diag_in_bound(self.x + 1) and self.piece_is_enemy(board.tiles[self.y - 1][self.x - 1]):
            moves.append(tiles[self.y - 1][self.x + 1])

        # print("Pawn moves: ")
        # print(moves)
        self.possible_moves = moves if len(moves) > 0 else None
        return moves if len(moves) > 0 else None
