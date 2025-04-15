import chess
import chess.pgn
import random
import pygame
import datetime
import os

from components.shared import BOARD, LAYERS, MOUSE
from components.render import render_board_bg, render_board, render_mouse_highlight, get_captured_surfaces, render_text, render_legal_moves
from components.mouse import get_mouse_square
from components.game.ends import get_game_result
from components.game.engine import do_move

pygame.init()

check_sound = pygame.mixer.Sound("sound/move-check.mp3")
move_opponent_sound = pygame.mixer.Sound("sound/move-opponent.mp3")
move_self_sound = pygame.mixer.Sound("sound/move-self.mp3")
capture_sound = pygame.mixer.Sound("sound/capture.mp3")
castle_sound = pygame.mixer.Sound("sound/castle.mp3")

def play_move_sound(board, move, white=True):
    test_board = board.copy()
    test_board.push(move)
    if test_board.is_checkmate():
        check_sound.play()
    elif test_board.is_check():
        check_sound.play()
    elif board.is_capture(move):
        capture_sound.play()
    elif test_board.is_castling(move):
        castle_sound.play()
    elif white:
        move_self_sound.play()
    else:
        move_opponent_sound.play()

def save_PGN(board):
    game = chess.pgn.Game.from_board(board)
    today = datetime.date.today() # get today's date as a string
    filename = f"games/{today}.pgn"
    if not os.path.exists("games"):
        os.makedirs("games") # create the directory if it doesn't exist
    with open(filename, "w") as f:
        print(game, file=f)
    

screen = pygame.display.set_mode((800, 600))
MOUSE = pygame.mouse
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
running = True

pygame.display.set_caption("tinychess")

LAYERS["boardbg"] = pygame.Surface((400, 400), pygame.SRCALPHA)
render_board_bg(LAYERS["boardbg"]) # this doesn't change so we can just do it once

LAYERS["pieces"] = pygame.Surface((400, 400), pygame.SRCALPHA)

LAYERS["boardui"] = pygame.Surface((400, 400), pygame.SRCALPHA)

LAYERS["legal_moves"] = pygame.Surface((400, 400), pygame.SRCALPHA)

LAYERS["screenui"] = pygame.Surface((800, 600), pygame.SRCALPHA)

LAYERS["moves_rank"] = pygame.Surface((200, 600), pygame.SRCALPHA)

BOARD_UNIT = pygame.Surface((400,400), pygame.SRCALPHA)

frame = 0
game_over = False
gen_next_move_flag = False
sel_square = None
piece_moves = []
piece_move_squares = []

mouse1 = False
clicking = False
clicked = False

while running:

    game_over, result = get_game_result(BOARD)
    if game_over:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        waiting = False
                        break
                    elif event.key == pygame.K_SPACE:
                        waiting = False
                        break

            save_PGN(BOARD)
            screen.fill((218, 177, 99))
            text_rect = font.render(result, True, (0, 0, 0)).get_rect(center=(400, 300))
            screen.blit(font.render(result, True, (0, 0, 0)), text_rect)

            press_space_rect = font.render("press SPACE to continue", True, (0, 0, 0)).get_rect(center=(400, 350))
            screen.blit(font.render("press SPACE to continue", True, (0, 0, 0)), press_space_rect)
            pygame.display.flip()
        BOARD.reset()
        game_over = False
        gen_next_move_flag = False
        continue

    if gen_next_move_flag and gen_next_move_timer == frame:
        move, bote_moves = do_move(BOARD)
        if move is None:
            continue
        play_move_sound(BOARD, move, BOARD.turn == chess.WHITE)
        BOARD.push(move)
        gen_next_move_flag = False
            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            elif event.key == pygame.K_SPACE:
                ...

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not clicking:
                    clicked = True 
                clicking = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:                       # mouse 1 up
                mouse1 = False                        # end the click
                clicking = False

    if clicked:
        square = get_mouse_square(MOUSE, (100, 100))

        if square is not None:
            if sel_square is not None and piece_moves:
                for move in piece_moves:
                    if move.to_square == square:
                        play_move_sound(BOARD, move, BOARD.turn == chess.WHITE)
                        BOARD.push(move)
                        sel_square = None
                        piece_moves = []
                        piece_move_squares = []
                        gen_next_move_flag = True
                        gen_next_move_timer = frame + random.randint(30, 120)
                        break
                else:
                    sel_square = None
                    piece_moves = []
                    piece_move_squares = []

            else:
                piece = BOARD.piece_at(square)
                if piece and piece.color == BOARD.turn:
                    sel_square = square
                    piece_moves = [move for move in BOARD.legal_moves if move.from_square == sel_square]
                    piece_move_squares = [move.to_square for move in piece_moves]
                else:
                    sel_square = None
                    piece_moves = []
                    piece_move_squares = []
        else:
            sel_square = None
            piece_moves = []
            piece_move_squares = []

        clicked = False

    BOARD_UNIT.fill((0, 0, 0, 0)) # clear the board unit surface
    BOARD_UNIT.blit(LAYERS["boardbg"], (0, 0))

    LAYERS["pieces"].fill((0, 0, 0, 0)) 
    render_board(LAYERS["pieces"], BOARD)
    BOARD_UNIT.blit(LAYERS["pieces"], (0, 0))

    screen.fill((218, 177, 99))
    pygame.draw.rect(screen, (0, 0, 0), (80, 80, 440, 440), 0)

    LAYERS["boardui"].fill((0, 0, 0, 0)) # clear the ui surface
    render_mouse_highlight(LAYERS["boardui"], MOUSE, (100, 100))
    BOARD_UNIT.blit(LAYERS["boardui"], (0, 0))

    white_captured, black_captured = get_captured_surfaces(BOARD)

    LAYERS["legal_moves"].fill((0, 0, 0, 0)) # clear the legal moves surface
    render_legal_moves(LAYERS["legal_moves"], piece_moves)
    BOARD_UNIT.blit(LAYERS["legal_moves"], (0, 0))
    
    LAYERS["screenui"].fill((0, 0, 0, 0)) # clear the ui surface
    LAYERS["screenui"].blit(white_captured, (100, 30))
    LAYERS["screenui"].blit(black_captured, (100, 520))

    version_text_rect = font.render("tinychess i1", True, (0, 0, 0)).get_rect(topright=(800, 0))
    LAYERS["screenui"].blit(font.render("tinychess i1", True, (0, 0, 0)), version_text_rect)

    mouse_square = get_mouse_square(MOUSE, (100, 100))
    if mouse_square is not None:
        render_text(LAYERS["screenui"], font, chess.square_name(mouse_square), (0, 0))

    screen.blit(BOARD_UNIT, (100, 100))
    screen.blit(LAYERS["screenui"], (0, 0))

    screen.blit(LAYERS["moves_rank"], (600, 0))

    frame += 1


    pygame.display.flip()
    clock.tick(60)