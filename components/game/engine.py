import chess
import copy
import random

from components.shared import PIECES_VALUES_INVERSE, PIECES_VALUES

white_openings = [
    "e4", "d4", "Nf3", "c4", "f4", "b3"
]

black_openings = [
    "e5", "c5", "e6", "c6", "d5", "g6", "Nf6"
]

def get_legal_moves(board):
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    return legal_moves

def get_pieces(board, colour, mode="piece"):
    my_squares = board.occupied_co[colour]
    my_squares = chess.SquareSet(my_squares) # convert to squareset
    my_squares = list(my_squares) # convert to list

    if mode == "type":
        my_pieces = [board.piece_at(square).piece_type for square in my_squares]
    elif mode == "piece":
        my_pieces = [board.piece_at(square) for square in my_squares]
    elif mode == "square":
        return my_squares

    raise ValueError("invalid mode for get_pieces")

def do_move(board):
    
    legal_moves = get_legal_moves(board)
    if not legal_moves:
        return None
    
    move_number = board.fullmove_number

    
    me = board.turn
    opponent = not me

    if move_number == 1: # first move
        if me == chess.WHITE:
            move = board.parse_san(random.choice(white_openings))
        else:
            move = board.parse_san(random.choice(black_openings))

        return move, [(move, 0)]

    scored_moves = []

    for move in legal_moves:
        score = get_move_goodness(board, move, me)
        scored_moves.append((move, score))

    scored_moves.sort(key=lambda x: x[1], reverse=True) # sort by score

    best_score = scored_moves[0][1] # the best score

    best_moves = [move for move, score in scored_moves if score == best_score] # all moves with the best score

    move = random.choice(best_moves) # pick one of the best moves at random

    return move, scored_moves

    
def get_move_goodness(board, move, colour):
    score = 0

    imaginary_board = board.copy()
    imaginary_board.push(move) # this is a copy of the board after the move is made

    opponent_check, opponent_checkmate, oppponent_stalemate = can_opponent_end_game(imaginary_board, move, colour)
    if opponent_checkmate:
        score -= 5000 # we lose immediately
    elif opponent_check:
        score -= 5 # not necessarily a disaster but not ideal
    elif oppponent_stalemate:
        if do_i_want_stalemate(board, colour):
            score += 2500 # better than losing
        else:
            score -= 2500 # worse than losing

    if imaginary_board.is_check():
        if is_piece_adequately_defended(imaginary_board, move.to_square, colour):
            score += 10
        else:
            score -= 10 # don't give away a piece like an idiot
    if imaginary_board.is_checkmate():
        score += 5000 # we win immediately
    if imaginary_board.is_stalemate():
        if do_i_want_stalemate(board, colour):
            score += 2500 # better than losing
        else:
            score -= 2500 # worse than losing

    if move.promotion is not None:
        promoted_piece_type = move.promotion
        if is_piece_adequately_defended(imaginary_board, move.to_square, colour):
            score += PIECES_VALUES[promoted_piece_type] # we gain the piece
        else:
            score -= (PIECES_VALUES[promoted_piece_type] + PIECES_VALUES[chess.PAWN]) # we lose the piece and the pawn in a sense

    if board.is_capture(move):
        if board.is_en_passant(move):
            captured_piece = chess.PAWN
        else:
            captured_piece = board.piece_at(move.to_square).piece_type
        capturing_piece = board.piece_at(move.from_square).piece_type
        captured_value = PIECES_VALUES[captured_piece]
        capturing_value = PIECES_VALUES[capturing_piece]

        if captured_value > capturing_value:
            score += captured_value - capturing_value
        else:
            if is_piece_adequately_defended(imaginary_board, move.to_square, colour):
                score += captured_value - capturing_value # we gain a piece
            else:
                score -= captured_value - capturing_value # we lose a piece

    if is_piece_adequately_defended(imaginary_board, move.to_square, colour):
        score += 1 # we're moving to a square that is either defended or not attacked
    else:
        score -= PIECES_VALUES[imaginary_board.piece_at(move.to_square).piece_type] # we're moving to a square that is attacked and not defended

    if board.piece_at(move.from_square).piece_type == chess.KING:
        if imaginary_board.is_castling(move):
            score += 2 # castling is good
        else:
            score -= 2 # don't move the king around like an idiot

    score -= value_of_pieces_hanging(imaginary_board, colour) # any pieces we hang we might as well be losing
    score += value_of_opponent_pieces_hanging(imaginary_board, colour) // 2 # any pieces they hang we might as well be gaining
    # i'm halving this because it seems to incentivise just leaving the opponent's pieces hanging and not taking them
    # (if they take the piece, there is less pieces hanging, so the score is lower)

    if moves_into_centre(move):
        score += 2 # controlling the centre is good

    return score

def value_of_pieces_hanging(board, colour):
    my_squares = get_pieces(board, colour, mode="square")

    value_hanging = 0
    for square in my_squares:
        if not is_piece_adequately_defended(board, square, colour):
            value_hanging += PIECES_VALUES[board.piece_at(square).piece_type]
    return value_hanging

def value_of_opponent_pieces_hanging(board, colour):
    return value_of_pieces_hanging(board, not colour)

def moves_into_centre(move):
    from_square = move.from_square
    to_square = move.to_square

    from_x, from_y = chess.square_file(from_square), chess.square_rank(from_square)
    to_x, to_y = chess.square_file(to_square), chess.square_rank(to_square)

    if (from_x == 3 or from_x == 4) and (from_y == 3 or from_y == 4):
        return True
    if (to_x == 3 or to_x == 4) and (to_y == 3 or to_y == 4):
        return True
    return False

def do_i_want_stalemate(board, colour):
    my_pieces = get_pieces(board, colour, "type") # get all the piece types i have

    i_have_queen = any(piece == chess.QUEEN for piece in my_pieces)
    i_have_rook = any(piece == chess.ROOK for piece in my_pieces)
    i_have_pawn = any(piece == chess.PAWN for piece in my_pieces)
    # there's technically a way to win with multiple bishops or knights but it's tricky and i don't know how to do it

    if i_have_queen or i_have_rook or i_have_pawn: # there's still a chance to win
        return False
    else: # if I have no pieces left, i want to stalemate
        return True

def can_opponent_end_game(imaginary_board, move, colour): 
    legal_moves = get_legal_moves(imaginary_board)
    if not legal_moves:
        return False, False, False
    
    for opponent_move in legal_moves:
        double_imaginary_board = imaginary_board.copy() # we're two moves deep now
        double_imaginary_board.push(opponent_move)
        if double_imaginary_board.is_checkmate():
            return True, True, False
        if double_imaginary_board.is_check():
            return True, False, False
        if double_imaginary_board.is_stalemate():
            return False, False, True
    return False, False, False

def is_piece_adequately_defended(board, square, colour):
    piece = board.piece_at(square)
    if not piece:
        return False
    piece_type = piece.piece_type
    piece_value = PIECES_VALUES[piece_type]

    attacker_score = 0
    defender_score = 0

    attackersquares = board.attackers(not colour, square)
    attackers = []
    for attacker_square in attackersquares:
        attacker = board.piece_at(attacker_square).piece_type
        attackers.append(attacker)

    for attacker in attackers:
        attacker_score += PIECES_VALUES_INVERSE[attacker] # inverse value because a pawn is scarier than a queen in this situation
        attacker_value = PIECES_VALUES[attacker]
        if attacker_value < piece_value:
            return False

    defendersquares = board.attackers(colour, square)
    defenders = []
    for defender_square in defendersquares:
        defender = board.piece_at(defender_square).piece_type
        defenders.append(defender)

    for defender in defenders:
        defender_score += PIECES_VALUES_INVERSE[defender]

    if attacker_score > defender_score:
        return False
    else:
        return True

    

    

    
