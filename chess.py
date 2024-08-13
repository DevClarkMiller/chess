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

run = True
while run:
    screen.fill((255, 255, 255))  # Refreshes screen
    board.mask_layer.fill((0, 0, 0, 0))

    # Draws all the tiles and pieces on the board
    board.draw_board()

    # Gets all possible moves 
    board.set_possible_moves()

    mouse_pos = pygame.mouse.get_pos()
    board.set_mouse_rel(mouse_pos)  # Sets the relative mouse position to the coords on the board

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # print(f"Mouse click at: {board.mouse_pos}")
            for i in range(TILES_IN_ROW):
                for j in range(TILES_IN_ROW):
                    tile = board.tiles[i][j]
                    tile.check_click(board.mouse_pos)
        
    screen.blit(board.mask_layer, (0, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()