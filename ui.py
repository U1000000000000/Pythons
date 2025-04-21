import pygame
from settings import *

def show_score(score_left, score_right, label_left='Player', label_right='AI', font='times new roman', size=20):
    score_font = pygame.font.SysFont(font, size)

    left_surface = score_font.render(f'{label_left} Score: {score_left}', True, white)
    left_rect = left_surface.get_rect(topleft=(10, 10))
    pygame.display.get_surface().blit(left_surface, left_rect)

    right_surface = score_font.render(f'{label_right} Score: {score_right}', True, white)
    right_rect = right_surface.get_rect(topright=(window_x - 10, 10))
    pygame.display.get_surface().blit(right_surface, right_rect)

def show_countdown(remaining_time, font='times new roman', size=30):
    countdown_font = pygame.font.SysFont(font, size)
    countdown_surface = countdown_font.render(f'Time Left: {remaining_time}s', True, white)
    countdown_rect = countdown_surface.get_rect(center=(window_x // 2, 10))
    pygame.display.get_surface().blit(countdown_surface, countdown_rect)

def pause_game():
    paused_font = pygame.font.SysFont('times new roman', 30)
    paused_surface = paused_font.render('Game Paused. Press Space to Resume.', True, white)
    paused_rect = paused_surface.get_rect(center=(window_x // 2, window_y // 2))
    pygame.display.get_surface().blit(paused_surface, paused_rect)
    pygame.display.flip()

# Menu functions (difficulty, duration)
def show_difficulty_menu(selected_option):
    from pygame.display import get_surface
    surface = get_surface()
    surface.fill(black)
    font = pygame.font.SysFont('times new roman', 40)
    options = ['Easy', 'Medium', 'Hard']
    title_surface = font.render('Choose AI Difficulty:', True, white)
    title_rect = title_surface.get_rect(center=(window_x // 2, window_y // 4))
    surface.blit(title_surface, title_rect)

    for i, option in enumerate(options):
        option_surface = font.render(option, True, white)
        option_rect = option_surface.get_rect(center=(window_x // 2, window_y // 2 + i * 40))
        if i == selected_option:
            pointer_surface = font.render('->', True, white)
            pointer_rect = pointer_surface.get_rect(center=(window_x // 2 - 100, window_y // 2 + i * 40))
            surface.blit(pointer_surface, pointer_rect)
        surface.blit(option_surface, option_rect)

    pygame.display.update()

def show_start_menu(selected_option):
    from pygame.display import get_surface
    surface = get_surface()
    surface.fill(black)
    font = pygame.font.SysFont('times new roman', 40)
    options = ['30 Seconds', '60 Seconds', '90 Seconds']
    title_surface = font.render('Choose Game Duration:', True, white)
    title_rect = title_surface.get_rect(center=(window_x // 2, window_y // 4))
    surface.blit(title_surface, title_rect)

    for i, option in enumerate(options):
        option_surface = font.render(option, True, white)
        option_rect = option_surface.get_rect(center=(window_x // 2, window_y // 2 + i * 40))
        if i == selected_option:
            pointer_surface = font.render('->     ', True, white)
            pointer_rect = pointer_surface.get_rect(center=(window_x // 2 - 100, window_y // 2 + i * 40))
            surface.blit(pointer_surface, pointer_rect)
        surface.blit(option_surface, option_rect)

    pygame.display.update()


def show_mode_menu(selected_option):
    from pygame.display import get_surface
    surface = get_surface()
    surface.fill(black)
    font = pygame.font.SysFont('times new roman', 40)
    options = ['Play with Computer', 'Play with Friend']
    title_surface = font.render('Choose Game Mode:', True, white)
    title_rect = title_surface.get_rect(center=(window_x // 2, window_y // 4))
    surface.blit(title_surface, title_rect)

    for i, option in enumerate(options):
        option_surface = font.render(option, True, white)
        option_rect = option_surface.get_rect(center=(window_x // 2, window_y // 2 + i * 40))
        if i == selected_option:
            pointer_surface = font.render('->                  ', True, white)
            pointer_rect = pointer_surface.get_rect(center=(window_x // 2 - 100, window_y // 2 + i * 40))
            surface.blit(pointer_surface, pointer_rect)
        surface.blit(option_surface, option_rect)

    pygame.display.update()


def show_menu():
    selected_mode = 0
    selected_difficulty = 0
    selected_duration = 0
    choosing_mode = True
    choosing_difficulty = False
    choosing_duration = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if choosing_mode:
                    if event.key == pygame.K_UP:
                        selected_mode = (selected_mode - 1) % 2
                    elif event.key == pygame.K_DOWN:
                        selected_mode = (selected_mode + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        choosing_mode = False
                        if selected_mode == 0:
                            choosing_difficulty = True
                        else:
                            choosing_duration = True
                elif choosing_difficulty:
                    if event.key == pygame.K_UP:
                        selected_difficulty = (selected_difficulty - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        selected_difficulty = (selected_difficulty + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        choosing_difficulty = False
                        choosing_duration = True
                elif choosing_duration:
                    if event.key == pygame.K_UP:
                        selected_duration = (selected_duration - 1) % 3
                    elif event.key == pygame.K_DOWN:
                        selected_duration = (selected_duration + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        durations = [30, 60, 90]
                        difficulties = ['Easy', 'Medium', 'Hard']
                        if selected_mode == 0:
                            return 'ai', difficulties[selected_difficulty], durations[selected_duration]
                        else:
                            return 'friend', None, durations[selected_duration]

        if choosing_mode:
            show_mode_menu(selected_mode)
        elif choosing_difficulty:
            show_difficulty_menu(selected_difficulty)
        elif choosing_duration:
            show_start_menu(selected_duration)
