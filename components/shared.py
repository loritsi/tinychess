import chess
import pygame

BOARD = chess.Board()

PIECE_IMAGES = {
    chess.PAWN: {
        "white": pygame.image.load("pieces/w_pawn.png"),
        "black": pygame.image.load("pieces/b_pawn.png"),
    },
    chess.KNIGHT: {
        "white": pygame.image.load("pieces/w_knight.png"),
        "black": pygame.image.load("pieces/b_knight.png"),
    },
    chess.BISHOP: {
        "white": pygame.image.load("pieces/w_bishop.png"),
        "black": pygame.image.load("pieces/b_bishop.png"),
    },
    chess.ROOK: {
        "white": pygame.image.load("pieces/w_rook.png"),
        "black": pygame.image.load("pieces/b_rook.png"),
    },
    chess.QUEEN: {
        "white": pygame.image.load("pieces/w_queen.png"),
        "black": pygame.image.load("pieces/b_queen.png"),
    },
    chess.KING: {
        "white": pygame.image.load("pieces/w_king.png"),
        "black": pygame.image.load("pieces/b_king.png"),
    },
}

PIECES_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,
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