import pygame, chess_logic
from chess_board import Board
from globals import init_pieces_icons, TILES_IN_ROW
import chess_piece

pygame.init()

SCREEN_WIDTH = 700
SCREEN_HEIGHT = SCREEN_WIDTH
# SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Board")

clock = pygame.time.Clock()

# Board is set to takeup whole screen, but could be sized to whatever and placed wherever
# TODO - ACTUALLY ALLOW TO PLACE ANYWHERE/SCALE WITH SCREEN
board = Board(screen, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)  

# Populates a dict with the name of the file as key, and path as the value
# Must load this function before creating any pieces
init_pieces_icons('./pieces')

board.init_locations_dict("./starting_locations.json")
board.init_tiles()

active_tile = None
mouse_pos = None

run = True
while run:
    screen.fill((255, 255, 255))  # Refreshes screen
    board.mask_layer.fill((0, 0, 0, 0))


    # Gets all possible moves 
    board.set_possible_moves()

    # Draws all the tiles and pieces on the board
    board.draw_board()

    if active_tile != None:
        mouse_x, mouse_y = mouse_pos
        piece_img = active_tile.piece.img

        # Centers the dragged tile to the middle of the mouse
        img_width, img_height = piece_img.get_size()
        centered_x = mouse_x - img_width // 2
        centered_y = mouse_y - img_height // 2

        screen.blit(piece_img, (centered_x, centered_y))
        board.draw_possible_moves(active_tile.piece.possible_moves)

    mouse_pos = pygame.mouse.get_pos()
    board.set_mouse_rel(mouse_pos)  # Sets the relative mouse position to the coords on the board

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Get the tile at the relative mouse pos
                rel_x, rel_y = board.mouse_pos
                if board.tiles[rel_y][rel_x]:      
                    tile = board.tiles[rel_y][rel_x]
                    if tile.piece != None:
                        # Resets the being dragged state of whatever piece was picked up
                        if active_tile:
                            active_tile.piece.being_dragged = False

                        active_tile = tile
                        active_tile.piece.being_dragged = True

        # Check what the mouses new pos will be. If valid, then move here
        if event.type == pygame.MOUSEBUTTONUP and active_tile != None:
            rel_x, rel_y = board.mouse_pos
            active_tile.piece.being_dragged = False
            active_tile.piece.move(active_tile, board.tiles[rel_y][rel_x])
            active_tile = None

    screen.blit(board.mask_layer, (0, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()