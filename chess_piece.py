import pygame
from abc import ABC, abstractmethod
from globals import imgs_dict, TILES_IN_ROW, piece_values

class Piece:
    def __init__(self, x, y, width, height, color, piece):
        self.color = color
        self.piece_c = piece
        self.img = None

        # x and y are relative to the board
        self.x = x
        self.y = y

        # Just the width and height of the tiles
        self.width = width
        self.height = height

        self.being_dragged = False
        
        self.possible_moves = None

    def set_image(self):
        img_path = Piece.get_img_path(self.piece_c, self.color)
        if img_path:
            self.img = pygame.image.load(img_path)
            self.img = pygame.transform.scale(self.img, (self.width, self.height))
    
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
    # Returns the value of the move, which will be subtracted from the opposing players score on the board object
    def move(self, og_tile, tile): 
        if og_tile == tile: return

        # Func which checks if the piece is a pawn and is able to turn into a queen
        def queen_morphable(og_tile, move_tile):
            if og_tile.piece.piece_c == "p" and (move_tile.tile_y == 0 or move_tile.tile_y == 7):
                return True
            return False


        # Set the current piece on the new tile or morphs into a queen if possible
        tile.piece = self 
        if queen_morphable(og_tile, tile):
            tile.piece = Queen(og_tile.piece.color, tile.tile_x, tile.tile_y, self.width, self.height)
            tile.piece.set_image()

        tile.piece.set_coords((tile.tile_x, tile.tile_y))
        og_tile.piece = None    # Reset the tile you moved from

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

            # If the piece is a pawn, it can't move forward if there's an enemy in the way
            if can_move_x and can_move_y and self.tile_available(tiles[y][x]):
                if self.piece_c == "p" and tiles[y][x].piece:
                    return
                
                moves.append((x, y))
                num_moves += 1

                # The enemy is the farthest a piece can move to, so it breaks from the loop when one is reached
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

    # x, y, width, height, color, piece
    def copy(self):
        copy = type(self)(self.color, self.x, self.y, self.width, self.height)
        copy.being_dragged = self.being_dragged
        copy.img = self.img
        return copy

class King(Piece):
    def __init__(self, color, x, y, width, height):
        super(King, self).__init__(x, y, width, height, color, "k")

    # get_all_dirs works differently if the piece is a king,
    # so implementation of get_moves is the same as the queens
    def get_moves(self, board):
        moves = []
        self.get_all_dirs(moves, board.tiles)
        return moves if len(moves) > 0 else None

class Queen(Piece):
    def __init__(self, color, x, y, width, height):
        super(Queen, self).__init__(x, y, width, height, color, "q")

    def get_moves(self, board):
        moves = []
        self.get_all_dirs(moves, board.tiles)
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
        return moves if len(moves) > 0 else None

class Knight(Piece):
    def __init__(self, color, x, y, width, height):
        super(Knight, self).__init__(x, y, width, height, color, "n")

    # Gets moves in an l shaped pattern
    def get_moves(self, board):
        moves = []

        def get_l_move(x_mod, y_mod):
            new_x = self.x + x_mod
            new_y = self.y + y_mod
            if (0 <= new_x < TILES_IN_ROW) and (0 <= new_y < TILES_IN_ROW):
                if self.tile_available(board.tiles[new_y][new_x]):
                    moves.append((new_x, new_y))

        get_l_move(1, 2)    # Up right
        get_l_move(2, 1)    # Right up
        get_l_move(2, -1)   # Right down
        get_l_move(1, -2)   # Down right
        get_l_move(-1, -2)  # Down left
        get_l_move(-2, -1)  # Left down
        get_l_move(-2, 1)   # Left up
        get_l_move(-1, 2)   # Up left
        
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
        return moves if len(moves) > 0 else None

class Pawn(Piece):
    def __init__(self, color, x, y, width, height):
        super(Pawn, self).__init__(x, y, width, height, color, "p")

    def get_moves(self, board):
        # Checks only a few surrounding tiles for moves since the pawns moveset is very limited
        moves = []
        tiles = board.tiles

        y_mod = 1 if self.color == "b" else -1

        # 1. Get how many moves you can make forward
        self.get_omni_moves(0, y_mod, moves, tiles)          

        # 2. Check both diagonals
        upper_diag_in_bound = lambda x : 0 <= x < TILES_IN_ROW and 0 <= (self.y + y_mod) < TILES_IN_ROW
        
        if upper_diag_in_bound(self.x - 1) and self.piece_is_enemy(board.tiles[self.y + y_mod][self.x - 1]):
            moves.append((self.x - 1, self.y + y_mod))

        if upper_diag_in_bound(self.x + 1) and self.piece_is_enemy(board.tiles[self.y + y_mod][self.x + 1]):
            moves.append((self.x + 1, self.y + y_mod))

        return moves if len(moves) > 0 else None