from math import inf
import pygame, ai, threading, queue, sys, os
from chess_board import Board
from globals import init_pieces_icons, TILES_IN_ROW

pygame.init()

class Chess:
    def __init__(self):
        SCREEN_WIDTH = 700
        SCREEN_HEIGHT = SCREEN_WIDTH
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chess Board")
        self.clock = pygame.time.Clock()

        # Init thread stuff
        self.ai_move = queue.Queue()
        self.ai_move_arr = []
        self.lock = threading.Lock()

        # Creates the board
        self.board = Board(self.screen, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)  
        init_pieces_icons('./pieces') 
        self.board.init_locations_dict("./starting_locations.json")
        self.board.init_tiles()  

        self.determining_moves = False

    def determine_move(self):
        # Adds the minimax check onto the queue of the thread
        f = open("board-output.txt", "w")
        f.write("")
        f.close()
        self.determining_moves = True
        #self.ai_move.put(ai.minimax(self.board.copy(), 3, inf, -inf, True, "b")[0])
        self.ai_move_arr.append(ai.minimax(self.board.copy(), 3, inf, -inf, True, "b")[0])
        print("Just finished determining the ais moves!")
        sys.exit()  # Exit thread after a move is found

    def main_game(self):
        t = threading.Thread(target=self.determine_move)
        run = True
        mouse_pos = None
        active_tile = None

        while run and not self.board.game_over:
            self.screen.fill((255, 255, 255))  # Refreshes screen
            self.board.mask_layer.fill((0, 0, 0, 0))

            # Gets all possible moves 
            if self.board.active_player == "w":
                moves = self.board.get_possible_moves()
                self.board.possible_moves_dict = moves

            # Draws all the tiles and pieces on the board
            self.board.draw_board()
            self.board.check_mouse_hover()

            if active_tile != None:
                mouse_x, mouse_y = mouse_pos
                piece_img = active_tile.piece.img

                # Centers the dragged tile to the middle of the mouse
                img_width, img_height = piece_img.get_size()
                centered_x = mouse_x - img_width // 2
                centered_y = mouse_y - img_height // 2

                self.screen.blit(piece_img, (centered_x, centered_y))
                piece = active_tile.piece
                possible_moves = self.board.possible_moves_dict.get((piece.x, piece.y))
                if possible_moves != None:
                    self.board.draw_possible_moves(possible_moves)

            mouse_pos = pygame.mouse.get_pos()
            self.board.set_mouse_rel(mouse_pos)  # Sets the relative mouse position to the coords on the board

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Get the tile at the relative mouse pos
                        rel_x, rel_y = self.board.mouse_pos
                        if self.board.tiles[rel_y][rel_x]:      
                            tile = self.board.tiles[rel_y][rel_x]
                            if tile.piece != None and tile.piece.color == "w" and tile.piece.color == self.board.active_player:
                                # Resets the being dragged state of whatever piece was picked up
                                if active_tile:
                                    active_tile.piece.being_dragged = False

                                active_tile = tile
                                active_tile.piece.being_dragged = True

                # Check what the mouses new pos will be. If valid, then move here
                if event.type == pygame.MOUSEBUTTONUP and active_tile != None:
                    rel_x, rel_y = self.board.mouse_pos
                    active_tile.piece.being_dragged = False
                    if Board.coord_in_board(self.board.mouse_pos): 
                        # active_tile.piece.move(active_tile, board.tiles[rel_y][rel_x])
                        from_coord = (active_tile.tile_x, active_tile.tile_y)
                        if self.board.player_move((from_coord, (rel_x, rel_y))):
                            print("Player made move")
                            self.board.next_turn()
                        active_tile = None
                
            # Tell ai to determine their move
            #self.lock.acquire()
            with self.lock:
                if (self.board.active_player == "b" 
                    #and self.ai_move.qsize() == 0 
                    and len(self.ai_move_arr) == 0
                    and not self.board.game_over
                    and not t.is_alive()
                    and not self.determining_moves):

                    # Remake thread
                    t = threading.Thread(target=self.determine_move)
                    t.start()
            #self.lock.release()

            # Make move if it's their turn and they've found a move
            if (self.board.active_player == "b"
                #and self.ai_move.qsize() > 0
                and len(self.ai_move_arr) > 0
                and not self.board.game_over):
                #move = self.ai_move.get()
                move = self.ai_move_arr[-1] 
                print(f"AI MOVING FROM {move[0]} TO {move[1]}")
                #print("AI NOW GOING TO MAKE MOVE")
                if move != None and move[0] != None and move[1] != None:
                    if self.board.make_move((move[0], move[1])):
                        self.board.next_turn()
                        self.ai_move_arr.pop()
                        self.determining_moves = False

            self.screen.blit(self.board.mask_layer, (0, 0))

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

# Starts game 
chess = Chess()
chess.main_game()