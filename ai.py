import random
from math import inf
from globals import TILES_IN_ROW

# def random_move(board):
#     moves = board.get_possible_moves()

#     # Select random key

#     # Select random element from the dicts key value

def output_board(board, f):
    # Implement this function to print your board in a readable format
    # For example, if your board is a 2D list, you can loop through and print each row
    for row in range(0, TILES_IN_ROW):
        for col in range(0, TILES_IN_ROW):
            tile = board.tiles[row][col]
            if tile.piece:
                f.write(f"[{tile.piece.piece_c}]")
            else:
                f.write("[ ]")
        f.write("\n")
    f.write("\n")

    f.close()

def evaluate(board, maximizing_color):
    if maximizing_color == "w":
        return board.white_score - board.black_score
    else:
        return board.black_score - board.white_score

def minimax(board, depth, alpha, beta, maximizing_player, maximizing_color):
    #board.print_details()
    if depth == 0 or board.game_over:
        f = open("board-output.txt", "a")
        f.write(f"Depth: {depth}, Evaluation: {evaluate(board, maximizing_color)}\n")
        output_board(board, f)
        return None, evaluate(board, maximizing_color)  # Only returns the evaluation at depth 0
    
    from_moves = board.get_possible_moves(board.active_player) # Give this parameter so that the 
    if len(from_moves) == 0:
        print("NO MOVES AVAILABLE")
        return None, None
    
    # Get a random key
    # random_key = random.choice(list(from_moves))
    # random_move = random.choice(from_moves.get(random_key))
    # best_move = (random_key, random_move)
    best_move = None

    # Find maximum value
    if maximizing_player:
        max_eval = -inf # Worse possible scenario
        for from_move in from_moves:    # Iterate over all the keys
            to_moves = from_moves[from_move]
            for to_move in to_moves:
                board.make_move((from_move, to_move))
                current_eval = minimax(board, depth - 1, alpha, beta, False, maximizing_color)[1]
                board.unmake_move()
                if current_eval > max_eval:
                    max_eval = current_eval
                    # if current_eval != 0:
                    best_move = (from_move, to_move)

                alpha = max(alpha, current_eval)
                if beta <= alpha:
                    break
        return best_move, max_eval
    # Find minumum value
    else:
        min_eval = inf
        for from_move in from_moves:    # Iterate over all the keys
            to_moves = from_moves[from_move]
            for to_move in to_moves:
                board.make_move((from_move, to_move))
                current_eval = minimax(board, depth - 1, alpha, beta, True, maximizing_color)[1]
                board.unmake_move()
                if current_eval < min_eval:
                    min_eval = current_eval
                    # if current_eval != 0:
                    best_move = (from_move, to_move)

                beta = min(beta, current_eval)
                if beta <= alpha:
                    break
        return best_move, min_eval