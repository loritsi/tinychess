import chess

def get_game_result(board):
    if not board.is_game_over():
        return False, ""

    if board.is_checkmate():
        winner = "white" if board.turn == chess.BLACK else "black"
        return True, f"{winner} wins by checkmate"
    elif board.is_stalemate():
        return True, "draw by stalemate"
    elif board.is_insufficient_material():
        return True, "draw by insufficient material"
    elif board.is_seventyfive_moves():
        return True, "draw by 75-move rule"
    elif board.is_fivefold_repetition():
        return True, "draw by fivefold repetition"
    else:
        return True, "draw (other reason)"
    


