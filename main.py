import pygame
from settings import *
from ui import show_menu
from game_ai import game_loop_vs_ai
from game_friend import game_loop_vs_friend

pygame.init()
pygame.display.set_mode((window_x, window_y))
pygame.display.set_caption('Snake Game')

mode, difficulty, duration = show_menu()

if mode == 'ai':
    game_loop_vs_ai(difficulty, duration)
else:
    game_loop_vs_friend(duration)
