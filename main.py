import chess
import chess.pgn
import random
import pygame
import datetime
import os
import sys

from components.shared import BOARD, LAYERS, MOUSE, SCREEN_MODE, FLIP_BOARD, VERSION, PLAYER
from components.render import render_board_bg, render_board, render_mouse_highlight, get_captured_surfaces, render_text, render_legal_moves
from components.mouse import get_mouse_square
from components.game.ends import get_game_result
from components.game.engine import do_move
from components.button import Button
from components.thinkingthread import BackgroundTask

def resource_path(relative_path):
    # this works for dev and when using pyinstaller
    try:
        base_path = sys._MEIPASS  # pyinstaller sets this
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()

icon_surf = pygame.image.load(resource_path("assets/pieces/w_king.png"))
scaled_icon = pygame.transform.scale(icon_surf, (32, 32))
pygame.display.set_icon(scaled_icon)

check_sound = pygame.mixer.Sound(resource_path("assets/sound/move-check.mp3"))
move_opponent_sound = pygame.mixer.Sound(resource_path("assets/sound/move-opponent.mp3"))
move_self_sound = pygame.mixer.Sound(resource_path("assets/sound/move-self.mp3"))
capture_sound = pygame.mixer.Sound(resource_path("assets/sound/capture.mp3"))
castle_sound = pygame.mixer.Sound(resource_path("assets/sound/castle.mp3"))

title_image = pygame.image.load(resource_path("assets/title.png"))
title_width, title_height = title_image.get_size()
title_image = pygame.transform.scale(title_image, (title_width * 4, title_height * 4))

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
    time = datetime.datetime.now().strftime("%H-%M-%S") # get the current time as a string
    today = f"{today} {time}" # combine the date and time strings
    today = today.replace(" ", "_") # replace spaces with underscores
    filename = f"games/{today}.pgn"
    if not os.path.exists("games"):
        os.makedirs("games") # create the directory if it doesn't exist
    with open(filename, "w") as f:
        print(game, file=f)
    

screen = pygame.display.set_mode((800, 600))
MOUSE = pygame.mouse
clock = pygame.time.Clock()

font = pygame.font.Font(resource_path("assets/font/semibold.otf"), 30)
running = True

pygame.display.set_caption("tinychess")

LAYERS["boardbg"] = pygame.Surface((400, 400), pygame.SRCALPHA)

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

def game_as_white(dummy):
    global SCREEN_MODE, FLIP_BOARD, clicking, clicked, gen_next_move_flag, gen_next_move_timer, PLAYER
    PLAYER = chess.WHITE
    gen_next_move_flag = False
    gen_next_move_timer = 0
    FLIP_BOARD = False
    SCREEN_MODE = "game"
    clicking = False
    clicked = False

def game_as_black(dummy):
    global SCREEN_MODE, FLIP_BOARD, gen_next_move_flag, gen_next_move_timer, clicking, clicked, PLAYER
    PLAYER = chess.BLACK
    FLIP_BOARD = True
    SCREEN_MODE = "game"
    gen_next_move_flag = True
    gen_next_move_timer = frame + random.randint(60, 60)
    clicking = False
    clicked = False

def go_menu(dummy):
    global SCREEN_MODE, clicking, clicked, game_over
    SCREEN_MODE = "menu"
    if BOARD.is_game_over():
        save_PGN(BOARD)
    BOARD.reset()
    game_over = False
    clicking = False
    clicked = False

def takeback(dummy):
    print("takeback clicked")
    global BOARD, gen_next_move_flag, gen_next_move_timer, clicking, clicked, game_over
    if (BOARD.turn == PLAYER) and BOARD.move_stack and (BOARD.fullmove_number > 1):
        # only allow takeback if the player is the one to move and there are moves to take back
        BOARD.pop()
        BOARD.pop()
        gen_next_move_flag = False
        gen_next_move_timer = 0
        game_over = False
    else:
        print("takeback not allowed")
        print("player:", PLAYER)
        print("turn:", BOARD.turn)
    clicking = False
    clicked = False
    return

TAKEBACK_BUTTON = Button(
    text="takeback",
    textcolour=(0, 0, 0),
    window=screen,
    buttonfont=font,
    x= screen.get_width() - 225,
    y= screen.get_height() - 110,
    function=takeback,
    args=None,
    width=200,
    height=50
)

WHITE_BUTTON = Button(
    text="play game as white",
    textcolour=(0, 0, 0),
    window=screen,
    buttonfont=font,
    x= screen.get_width()/2 - 200,
    y= screen.get_height()/2 + 50,
    function=game_as_white,
    args=None,
    width=400,
    height=50
)

BLACK_BUTTON = Button(
    text="play game as black",
    textcolour=(0, 0, 0),
    window=screen,
    buttonfont=font,
    x= screen.get_width()/2 - 200,
    y= screen.get_height()/2 + 150,
    function=game_as_black,
    args=None,
    width=400,
    height=50
)

MENU_BUTTON = Button(
    text="back to menu",
    textcolour=(0, 0, 0),
    window=screen,
    buttonfont=font,
    x= screen.get_width()-300,
    y= screen.get_height()-50,
    function=go_menu,
    args=None,
    width=300,
    height=50
)

move_task = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            if move_task:
                move_task = None
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if move_task:
                move_task = None
                break
            elif event.key == pygame.K_b:
                FLIP_BOARD = not FLIP_BOARD
                print(f"{FLIP_BOARD}")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not clicking:
                    clicked = True 
                clicking = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:                       # mouse 1 up
                mouse1 = False                        # end the click
                clicking = False


    if SCREEN_MODE == "menu":
        screen.fill((218, 177, 99))

        big_king = pygame.transform.scale(icon_surf, (64, 64))
        big_king_rect = big_king.get_rect(center=(400, 100))
        screen.blit(big_king, big_king_rect)

        title_image_rect = title_image.get_rect(center=(400, 200))
        screen.blit(title_image, title_image_rect)

        text_rect = font.render(f"version {VERSION}", True, (0, 0, 0)).get_rect(center=(400, 300))
        screen.blit(font.render(f"version {VERSION}", True, (0, 0, 0)), text_rect)
        
        WHITE_BUTTON.tick(MOUSE.get_pos(), clicking)
        WHITE_BUTTON.render()

        BLACK_BUTTON.tick(MOUSE.get_pos(), clicking)
        BLACK_BUTTON.render()
        
        pygame.display.flip()
        continue

    if SCREEN_MODE == "game_over": # forces only checking for menu button when game is over
        #TAKEBACK_BUTTON.tick(MOUSE.get_pos(), clicking)
        MENU_BUTTON.tick(MOUSE.get_pos(), clicking)
        clicked = False
        clicking = False

    game_over, result = get_game_result(BOARD)
    if game_over:
        MENU_BUTTON.tick(MOUSE.get_pos(), clicking)
        clicked = False
        clicking = False


    if gen_next_move_flag and gen_next_move_timer == frame and not game_over and not move_task:
        move_task = BackgroundTask(do_move, BOARD)

    if move_task and move_task.done:
        move, bote_moves = move_task.result()
        if move is None:
            move_task = None
            continue
        play_move_sound(BOARD, move, BOARD.turn == chess.WHITE)
        BOARD.push(move)
        move_task = None
        gen_next_move_flag = False
            


    if clicked and not game_over:
        square = get_mouse_square(MOUSE, (100, 100), flip=FLIP_BOARD)

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
                        gen_next_move_timer = frame + random.randint(60, 60)
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
    
    render_board_bg(LAYERS["boardbg"], FLIP_BOARD)

    BOARD_UNIT.fill((0, 0, 0, 0)) # clear the board unit surface
    BOARD_UNIT.blit(LAYERS["boardbg"], (0, 0))

    LAYERS["pieces"].fill((0, 0, 0, 0)) 
    render_board(LAYERS["pieces"], BOARD, FLIP_BOARD)
    BOARD_UNIT.blit(LAYERS["pieces"], (0, 0))

    screen.fill((218, 177, 99))
    pygame.draw.rect(screen, (0, 0, 0), (80, 80, 440, 440), 0, border_radius=10)

    LAYERS["boardui"].fill((0, 0, 0, 0)) # clear the ui surface
    render_mouse_highlight(LAYERS["boardui"], MOUSE, flip=FLIP_BOARD, board_pos=(100, 100))
    BOARD_UNIT.blit(LAYERS["boardui"], (0, 0))

    white_captured, black_captured = get_captured_surfaces(BOARD, FLIP_BOARD)

    LAYERS["legal_moves"].fill((0, 0, 0, 0)) # clear the legal moves surface
    render_legal_moves(LAYERS["legal_moves"], piece_moves, FLIP_BOARD)
    BOARD_UNIT.blit(LAYERS["legal_moves"], (0, 0))
    
    LAYERS["screenui"].fill((0, 0, 0, 0)) # clear the ui surface
    LAYERS["screenui"].blit(white_captured, (100, 30))
    LAYERS["screenui"].blit(black_captured, (100, 520))

    version_text_rect = font.render(f"tinychess {VERSION}", True, (0, 0, 0)).get_rect(topright=(800, 0))
    LAYERS["screenui"].blit(font.render(f"tinychess {VERSION}", True, (0, 0, 0)), version_text_rect)

    mouse_square = get_mouse_square(MOUSE, (100, 100), FLIP_BOARD)
    if mouse_square is not None:
        render_text(LAYERS["screenui"], font, chess.square_name(mouse_square), (0, 0))

    screen.blit(BOARD_UNIT, (100, 100))
    screen.blit(LAYERS["screenui"], (0, 0))

    screen.blit(LAYERS["moves_rank"], (600, 0))

    TAKEBACK_BUTTON.render()
    TAKEBACK_BUTTON.tick(MOUSE.get_pos(), clicking)

    MENU_BUTTON.render()
    MENU_BUTTON.tick(MOUSE.get_pos(), clicking)

    if gen_next_move_flag and not game_over:
        gen_next_move_text = font.render("thinking...", True, (255, 255, 255)).get_rect(center=(650, 200))
        pygame.draw.rect(screen, (0, 0, 0), gen_next_move_text.inflate(20, 20), border_radius=10)
        screen.blit(font.render("thinking...", True, (255, 255, 255)), gen_next_move_text)

    if game_over:
        _, result = get_game_result(BOARD)
        result_text = "game over: " + result

        result_text_rect = font.render(result_text, True, (255, 255, 255)).get_rect(center=(400, 50))

        pygame.draw.rect(screen, (0, 0, 0), result_text_rect.inflate(20, 20), border_radius=10)
        screen.blit(font.render(result_text, True, (255, 255, 255)), result_text_rect)

    frame += 1


    pygame.display.flip()
    clock.tick(60)