import time
import pygame
from settings import *

def game_over(score, ai_score, player_crashed=False):
    font = pygame.font.SysFont('times new roman', 50)
    win_surface = font.render(f'Your Score is : {score}', True, red)
    win_rect = win_surface.get_rect(midtop=(window_x / 2, window_y / 4))
    pygame.display.get_surface().blit(win_surface, win_rect)

    winner_font = pygame.font.SysFont('times new roman', 40)
    if player_crashed:
        winner_text = 'AI Wins!'
    elif score > ai_score:
        winner_text = 'You Win!'
    elif score < ai_score:
        winner_text = 'AI Wins!'
    else:
        winner_text = 'It\'s a Tie!'

    winner_surface = winner_font.render(winner_text, True, white)
    winner_rect = winner_surface.get_rect(center=(window_x // 2, window_y // 2))
    pygame.display.get_surface().blit(winner_surface, winner_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()
