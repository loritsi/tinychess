import chess
import random
import pygame

from components.shared import BOARD, LAYERS, MOUSE
from components.render import render_board_bg, render_board, render_mouse_highlight, get_captured_surfaces, render_text
from components.mouse import get_mouse_square
from components.game.ends import get_game_result
from components.game.engine import do_move

pygame.init()

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

LAYERS["screenui"] = pygame.Surface((800, 600), pygame.SRCALPHA)

LAYERS["moves_rank"] = pygame.Surface((200, 600), pygame.SRCALPHA)

BOARD_UNIT = pygame.Surface((400,400), pygame.SRCALPHA)

frame = 0
game_over = False
gen_next_move_flag = True

while running:

    if gen_next_move_flag:
        move, best_moves = do_move(BOARD)
        to_move = "white" if BOARD.turn == chess.WHITE else "black"
        if move is not None:
            LAYERS["moves_rank"].fill((0, 0, 0, 0)) # clear the moves rank surface for new moves
            moves_str_list = [f"{BOARD.san(best_move[0])}: {best_move[1]}" for best_move in best_moves]
            print(f"best moves for {to_move}: {', '.join(moves_str_list)}")
            for i, move_str in enumerate(moves_str_list):
                render_text(LAYERS["moves_rank"], font, move_str, (0, i * 21))
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

                game_over, result = get_game_result(BOARD)

                if not game_over:
                    try:
                        fullmove = BOARD.fullmove_number
                        move_san = BOARD.san(move)
                        to_move = BOARD.piece_at(move.from_square).color
                        to_move = "white" if to_move == chess.WHITE else "black"
                        not_to_move = "black" if to_move == "white" else "white"
                        gen_next_move_flag = True
                        print(f"[{fullmove}] {to_move}: {move_san}") 
                    except Exception as e:
                        print(f"error: {e}")
                        gen_next_move_flag = True
                    BOARD.push(move)
                else:
                    print(f"game over! {result}")
                    gen_next_move_flag = True  
                    BOARD.reset()

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


    
    LAYERS["screenui"].fill((0, 0, 0, 0)) # clear the ui surface
    LAYERS["screenui"].blit(white_captured, (100, 30))
    LAYERS["screenui"].blit(black_captured, (100, 520))

    mouse_square = get_mouse_square(MOUSE, (100, 100))
    if mouse_square is not None:
        render_text(LAYERS["screenui"], font, chess.square_name(mouse_square), (0, 0))

    screen.blit(BOARD_UNIT, (100, 100))
    screen.blit(LAYERS["screenui"], (0, 0))

    screen.blit(LAYERS["moves_rank"], (600, 0))

    frame += 1


    pygame.display.flip()
    clock.tick(60)