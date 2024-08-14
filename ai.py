import random
from math import inf

def random_move(board):
    moves = board.get_possible_moves()

    # Select random key

    # Select random element from the dicts key value

def evaluate(board, maximizing_color):
    if maximizing_color == "w":
        return board.white_score - board.black_score
    else:
        return board.white_score - board.black_score

def minimax(board, depth, alpha, beta, maximizing_player, maximizing_color):
    if depth == 0 or board.game_over:
        return None, evaluate(board)
    
    from_moves = board.get_possible_moves()
    best_move = random.choice(from_moves)

    # Find maximum value
    if maximizing_player:
        max_eval = -inf # Worse possible scenario
        for from_move in from_moves:    # Iterate over all the keys
            to_moves = from_moves[from_move]
            for to_move in to_moves:
                board.make_move(from_move, to_move)
                current_eval = minimax(board, depth - 1, alpha, beta, False, maximizing_color)[1]
                board.unmake_move()
                if current_eval > max_eval:
                    max_eval = current_eval
                    best_move = to_move
        return best_move, max_eval
    # Find minumum value
    else:
        min_eval = inf
        for from_move in from_moves:    # Iterate over all the keys
            to_moves = from_moves[from_move]
            for to_move in to_moves:
                board.make_move(from_move, to_move)
                current_eval = minimax(board, depth - 1, alpha, beta, True, maximizing_color)[1]
                board.unmake_move()
                if current_eval < min_eval:
                    min_eval = current_eval
                    best_move = to_move
        return best_move, min_eval
