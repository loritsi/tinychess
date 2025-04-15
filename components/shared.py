import chess
import pygame
import os
import sys

BOARD = chess.Board()

def resource_path(relative_path):
    # this works for dev and when using pyinstaller
    try:
        base_path = sys._MEIPASS  # pyinstaller sets this
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

PIECE_IMAGES = {
    chess.PAWN: {
        "white": pygame.image.load(resource_path("pieces/w_pawn.png")),
        "black": pygame.image.load(resource_path("pieces/b_pawn.png")),
    },
    chess.KNIGHT: {
        "white": pygame.image.load(resource_path("pieces/w_knight.png")),
        "black": pygame.image.load(resource_path("pieces/b_knight.png")),
    },
    chess.BISHOP: {
        "white": pygame.image.load(resource_path("pieces/w_bishop.png")),
        "black": pygame.image.load(resource_path("pieces/b_bishop.png")),
    },
    chess.ROOK: {
        "white": pygame.image.load(resource_path("pieces/w_rook.png")),
        "black": pygame.image.load(resource_path("pieces/b_rook.png")),
    },
    chess.QUEEN: {
        "white": pygame.image.load(resource_path("pieces/w_queen.png")),
        "black": pygame.image.load(resource_path("pieces/b_queen.png")),
    },
    chess.KING: {
        "white": pygame.image.load(resource_path("pieces/w_king.png")),
        "black": pygame.image.load(resource_path("pieces/b_king.png")),
    },
}

PIECES_VALUES = { # adjusted values for ai evaluation
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 10,
    chess.QUEEN: 15,
    chess.KING: 0,
}

PIECES_VALUES_INVERSE = {
    chess.PAWN: 9,
    chess.KNIGHT: 4,
    chess.BISHOP: 4,
    chess.ROOK: 2,
    chess.QUEEN: 1,
    chess.KING: 0,
}

LAYERS = {}

MOUSE = None