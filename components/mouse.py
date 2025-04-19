import chess

def get_mouse_square(mouse, board_pos, flip):
    mouse_x, mouse_y = mouse.get_pos()
    board_x, board_y = board_pos
    square_x = (mouse_x - board_x) // 50
    square_y = (mouse_y - board_y) // 50

    if not flip:
        square_y = 7 - square_y
    else:
        square_x = 7 - square_x

    if 0 <= square_x < 8 and 0 <= square_y < 8:
        return chess.square(square_x, square_y)
    else:
        return None
