import pygame
import chess

from components.shared import PIECE_IMAGES, FLIP_BOARD
from components.mouse import get_mouse_square
from components.game.captures import get_captured_pieces

def render_board_bg(surface, flip):
    board_surf = pygame.Surface((8,8))
    for x in range(8):
        for y in range(8):
            if flip:
                color = (222, 206, 237) if (x + y) % 2 != 0 else (94, 91, 140)
            else:
                color = (222, 206, 237) if (x + y) % 2 == 0 else (94, 91, 140)
            board_surf.set_at((x, y), color)
    square = min(surface.get_width(), surface.get_height())
    board_surf = pygame.transform.scale(board_surf, (square, square))
    surface.blit(board_surf, (0, 0))
    return surface

def render_piece(surface, board, square, flip):
    piece = board.piece_at(square)
    if piece is None:
        return surface
    color = "white" if piece.color == chess.WHITE else "black"
    piece_image = PIECE_IMAGES[piece.piece_type][color]
    piece_image = pygame.transform.scale(piece_image, (48, 48))

    
    file, rank = chess.square_file(square), chess.square_rank(square)
    rank = (7 - rank) if not flip else rank
    file = (7 - file) if flip else file
    square_rect = pygame.Rect(file * 50, rank * 50, 50, 50)
    piece_rect = piece_image.get_rect(center=square_rect.center)
    surface.blit(piece_image, piece_rect.topleft)
    return surface

def render_legal_moves(surface, moves, flip):
    for move in moves:
        square = move.to_square
        file, rank = chess.square_file(square), chess.square_rank(square)
        rank = (7 - rank) if not flip else rank
        file = (7 - file) if flip else file

        square_rect = pygame.Rect(file * 50, rank * 50, 50, 50)
        legal_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(legal_surface, (0, 255, 0, 50), (25, 25), 20)
        surface.blit(legal_surface, square_rect.topleft)
    return surface

def render_board(surface, board, flip):
    for square in chess.SQUARES:
        render_piece(surface, board, square, flip)
    return surface

def render_light_at_square(surface, square: chess.square, flip):
    file, rank = chess.square_file(square), chess.square_rank(square)
    rank = (7 - rank) if not flip else rank
    file = (7 - file) if flip else file

    square_rect = pygame.Rect(file * 50, rank * 50, 50, 50)
    light_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
    light_surface.fill((255, 255, 0, 50))  # Semi-transparent yellow
    surface.blit(light_surface, square_rect.topleft)
    return surface

def render_mouse_highlight(surface, mouse, flip, board_pos=(0, 0)):
    square = get_mouse_square(mouse, board_pos, flip)
    if square == None:
        return surface
    render_light_at_square(surface, square, flip=flip)
    return surface

def render_piece_strip(pieces, colour):
    pieces_amount = len(pieces)
    surface = pygame.Surface((pieces_amount * 50, 50), pygame.SRCALPHA)
    for i, piece in enumerate(pieces):
        piece_image = PIECE_IMAGES[piece][colour].convert_alpha()
        piece_image = pygame.transform.scale(piece_image, (48, 48))
        surface.blit(piece_image, (i * 40, 0))
    return surface

def get_captured_surfaces(board, flip):
    captured_pieces = get_captured_pieces(board)
    white_pieces = []
    black_pieces = []
    for piece_type, count in captured_pieces["white"].items():
        white_pieces.extend([piece_type] * count)
    for piece_type, count in captured_pieces["black"].items():
        black_pieces.extend([piece_type] * count)

    if flip:
        white_surface = render_piece_strip(white_pieces, "black")
        black_surface = render_piece_strip(black_pieces, "white")
    else:
        white_surface = render_piece_strip(white_pieces, "white")
        black_surface = render_piece_strip(black_pieces, "black")
    return white_surface, black_surface

def render_text(surface, font, text, pos):
    text_surface = font.render(text, True, (255, 255, 255))
    surface.blit(text_surface, pos)
    return surface
