import chess

def get_captured_pieces(board):
    starting_counts = {
        "white": {
            chess.PAWN: 8,
            chess.KNIGHT: 2,
            chess.BISHOP: 2,
            chess.ROOK: 2,
            chess.QUEEN: 1,
            chess.KING: 1,
        },
        "black": {
            chess.PAWN: 8,
            chess.KNIGHT: 2,
            chess.BISHOP: 2,
            chess.ROOK: 2,
            chess.QUEEN: 1,
            chess.KING: 1,
        }
    }

    current_counts = {
        "white": {pt: 0 for pt in starting_counts["white"]},
        "black": {pt: 0 for pt in starting_counts["black"]},
    }

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            colour = "white" if piece.color == chess.WHITE else "black"
            current_counts[colour][piece.piece_type] += 1

    captured = {"white": {}, "black": {}}
    for colour in starting_counts:
        for piece_type in starting_counts[colour]:
            missing = starting_counts[colour][piece_type] - current_counts[colour][piece_type]
            if missing > 0:
                captured[colour][piece_type] = missing

    return captured