import pygame
import random
import time
from settings import *
from ui import show_score, show_countdown, pause_game

def game_over(p1_score, p2_score, p1_crashed=False, p2_crashed=False):
    game_window.fill(black)
    font = pygame.font.SysFont('times new roman', 40)

    if p1_crashed and not p2_crashed:
        text = "Player 2 Wins! (Player 1 Crashed)"
    elif p2_crashed and not p1_crashed:
        text = "Player 1 Wins! (Player 2 Crashed)"
    elif p1_crashed and p2_crashed:
        text = "Both Crashed! It's a Tie!"
    elif p1_score > p2_score:
        text = "Player 1 Wins!"
    elif p2_score > p1_score:
        text = "Player 2 Wins!"
    else:
        text = "It's a Tie!"

    text_surface = font.render(text, True, red)
    rect = text_surface.get_rect(center=(window_x // 2, window_y // 2))
    game_window.blit(text_surface, rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    quit()

def game_loop_vs_friend(duration):
    pygame.init()
    global game_window, fps
    game_window = pygame.display.set_mode((window_x, window_y))
    pygame.display.set_caption("Snake: Player vs Friend")
    fps = pygame.time.Clock()

    snake_speed = 15

    # Player 1
    p1_pos = [100, 50]
    p1_body = [[100, 50], [90, 50], [80, 50]]
    p1_dir = 'RIGHT'
    p1_change = p1_dir
    p1_score = 0



    # Player 2
    p2_pos = [400, 300]
    p2_body = [[400, 300], [410, 300], [420, 300]]
    p2_dir = 'LEFT'
    p2_change = p2_dir
    p2_score = 0

    fruit_pos = [random.randrange(1, (window_x // 10)) * 10,
                 random.randrange(1, (window_y // 10)) * 10]

    paused = False
    start_time = time.time()

    while True:
        elapsed_time = time.time() - start_time
        remaining_time = duration - int(elapsed_time)
        if remaining_time <= 0:
            game_over(p1_score, p2_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                # Player 1: Arrow keys
                if event.key == pygame.K_UP and p1_dir != 'DOWN':
                    p1_change = 'UP'
                elif event.key == pygame.K_DOWN and p1_dir != 'UP':
                    p1_change = 'DOWN'
                elif event.key == pygame.K_LEFT and p1_dir != 'RIGHT':
                    p1_change = 'LEFT'
                elif event.key == pygame.K_RIGHT and p1_dir != 'LEFT':
                    p1_change = 'RIGHT'
                # Player 2: WASD
                elif event.key == pygame.K_w and p2_dir != 'DOWN':
                    p2_change = 'UP'
                elif event.key == pygame.K_s and p2_dir != 'UP':
                    p2_change = 'DOWN'
                elif event.key == pygame.K_a and p2_dir != 'RIGHT':
                    p2_change = 'LEFT'
                elif event.key == pygame.K_d and p2_dir != 'LEFT':
                    p2_change = 'RIGHT'
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        pause_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        if paused:
            continue

        p1_dir = p1_change
        p2_dir = p2_change

        # Move Player 1
        if p1_dir == 'UP':
            p1_pos[1] -= 10
        elif p1_dir == 'DOWN':
            p1_pos[1] += 10
        elif p1_dir == 'LEFT':
            p1_pos[0] -= 10
        elif p1_dir == 'RIGHT':
            p1_pos[0] += 10

        # Move Player 2
        if p2_dir == 'UP':
            p2_pos[1] -= 10
        elif p2_dir == 'DOWN':
            p2_pos[1] += 10
        elif p2_dir == 'LEFT':
            p2_pos[0] -= 10
        elif p2_dir == 'RIGHT':
            p2_pos[0] += 10

        p1_body.insert(0, list(p1_pos))
        p2_body.insert(0, list(p2_pos))

        # Check fruit collision
        if p1_pos == fruit_pos:
            p1_score += 10
            fruit_pos = [random.randrange(1, (window_x // 10)) * 10,
                         random.randrange(1, (window_y // 10)) * 10]
        else:
            p1_body.pop()

        if p2_pos == fruit_pos:
            p2_score += 10
            fruit_pos = [random.randrange(1, (window_x // 10)) * 10,
                         random.randrange(1, (window_y // 10)) * 10]
        else:
            p2_body.pop()

        # Crash detection
        p1_crashed = (p1_pos[0] < 0 or p1_pos[0] >= window_x or
                      p1_pos[1] < 0 or p1_pos[1] >= window_y or
                      p1_pos in p1_body[1:] or
                      p1_pos in p2_body)

        p2_crashed = (p2_pos[0] < 0 or p2_pos[0] >= window_x or
                      p2_pos[1] < 0 or p2_pos[1] >= window_y or
                      p2_pos in p2_body[1:] or
                      p2_pos in p1_body)

        if p1_crashed or p2_crashed:
            game_over(p1_score, p2_score, p1_crashed, p2_crashed)

        # Draw
        game_window.fill(black)
        for block in p1_body:
            pygame.draw.rect(game_window, green, pygame.Rect(block[0], block[1], 10, 10))
        for block in p2_body:
            pygame.draw.rect(game_window, blue, pygame.Rect(block[0], block[1], 10, 10))
        pygame.draw.rect(game_window, white, pygame.Rect(fruit_pos[0], fruit_pos[1], 10, 10))

        show_score(p1_score, p2_score, label_left='Player 1', label_right='Player 2')
        show_countdown(remaining_time)
        pygame.display.update()
        fps.tick(snake_speed)
