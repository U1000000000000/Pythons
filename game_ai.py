import pygame
import random
import time
from settings import *
from ui import show_score, show_countdown, pause_game

def ai_snake_move(ai_pos, ai_body, direction, fruit_pos, difficulty):
    def is_safe(pos, ai_body):
        x, y = pos
        return (0 <= x < window_x and 0 <= y < window_y and pos not in ai_body)

    directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    move_offsets = {
        'UP': (0, -10),
        'DOWN': (0, 10),
        'LEFT': (-10, 0),
        'RIGHT': (10, 0)
    }

    def get_next_pos(direction):
        dx, dy = move_offsets[direction]
        return [ai_pos[0] + dx, ai_pos[1] + dy]

    if difficulty == 'Easy':
        # Random move with 40% chance
        if random.random() < 0.4:
            direction = random.choice(directions)
        else:
            if fruit_pos[0] > ai_pos[0] and direction != 'LEFT':
                direction = 'RIGHT'
            elif fruit_pos[0] < ai_pos[0] and direction != 'RIGHT':
                direction = 'LEFT'
            elif fruit_pos[1] > ai_pos[1] and direction != 'UP':
                direction = 'DOWN'
            elif fruit_pos[1] < ai_pos[1] and direction != 'DOWN':
                direction = 'UP'

    elif difficulty == 'Medium':
        # Go toward fruit with some randomness
        if random.random() < 0.1:
            direction = random.choice(directions)
        else:
            if fruit_pos[0] > ai_pos[0] and direction != 'LEFT':
                direction = 'RIGHT'
            elif fruit_pos[0] < ai_pos[0] and direction != 'RIGHT':
                direction = 'LEFT'
            elif fruit_pos[1] > ai_pos[1] and direction != 'UP':
                direction = 'DOWN'
            elif fruit_pos[1] < ai_pos[1] and direction != 'DOWN':
                direction = 'UP'

    elif difficulty == 'Hard':
        # Greedy logic with wall and self-body avoidance
        best_direction = direction
        min_distance = float('inf')
        for d in directions:
            next_pos = get_next_pos(d)
            if is_safe(next_pos, ai_body):
                dist = abs(next_pos[0] - fruit_pos[0]) + abs(next_pos[1] - fruit_pos[1])
                if dist < min_distance:
                    min_distance = dist
                    best_direction = d
        direction = best_direction

    # Move in the selected direction
    dx, dy = move_offsets[direction]
    ai_pos[0] += dx
    ai_pos[1] += dy
    ai_body.insert(0, list(ai_pos))

    return direction, ai_pos, ai_body

def game_over(player_score, ai_score, player_crashed=False, ai_crashed=False):
    game_window.fill(black)
    font = pygame.font.SysFont('times new roman', 40)
    if player_crashed:
        text = "You Crashed!, AI Wins!"
    elif ai_crashed:
        text = "AI Crashed!!!, You Win!"
    elif player_score > ai_score:
        text = "You Win!"
    elif player_score < ai_score:
        text = "AI Wins!"
    else:
        text = "It's a Tie!"

    text_surface = font.render(text, True, red)
    rect = text_surface.get_rect(center=(window_x//2, window_y//2))
    game_window.blit(text_surface, rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    quit()

def game_loop_vs_ai(difficulty, duration):
    pygame.init()
    global game_window, fps
    game_window = pygame.display.set_mode((window_x, window_y))
    pygame.display.set_caption("Snake vs AI")
    fps = pygame.time.Clock()

    # Speed based on difficulty
    snake_speed = {'Easy': 10, 'Medium': 15, 'Hard': 20}[difficulty]

    # Player Snake
    player_pos = [100, 50]
    player_body = [[100, 50], [90, 50], [80, 50]]
    direction = 'RIGHT'
    change_to = direction
    player_score = 0

    # AI Snake
    ai_pos = [400, 300]
    ai_body = [[400, 300], [390, 300], [380, 300]]
    ai_direction = 'LEFT'
    ai_score = 0

    # Fruit
    fruit_pos = [random.randrange(1, (window_x // 10)) * 10,
                 random.randrange(1, (window_y // 10)) * 10]

    start_time = time.time()
    paused = False

    while True:
        elapsed_time = time.time() - start_time
        remaining_time = duration - int(elapsed_time)
        if remaining_time <= 0:
            game_over(player_score, ai_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                    change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    change_to = 'RIGHT'
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                    if paused:
                        pause_game()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        if paused:
            continue

        direction = change_to

        # Move player
        if direction == 'UP':
            player_pos[1] -= 10
        elif direction == 'DOWN':
            player_pos[1] += 10
        elif direction == 'LEFT':
            player_pos[0] -= 10
        elif direction == 'RIGHT':
            player_pos[0] += 10

        player_body.insert(0, list(player_pos))

        if player_pos == fruit_pos:
            player_score += 10
            fruit_pos = [random.randrange(1, (window_x // 10)) * 10,
                         random.randrange(1, (window_y // 10)) * 10]
        else:
            player_body.pop()

        # Check player collision
        if (player_pos[0] < 0 or player_pos[0] >= window_x or
            player_pos[1] < 0 or player_pos[1] >= window_y or
            player_pos in player_body[1:]):
            game_over(player_score, ai_score, player_crashed=True)

        # AI Move
        ai_direction, ai_pos, ai_body = ai_snake_move(ai_pos, ai_body, ai_direction, fruit_pos, difficulty)

        if ai_pos == fruit_pos:
            ai_score += 10
            fruit_pos = [random.randrange(1, (window_x // 10)) * 10,
                         random.randrange(1, (window_y // 10)) * 10]
        else:
            ai_body.pop()

        if (ai_pos[0] < 0 or ai_pos[0] >= window_x or
            ai_pos[1] < 0 or ai_pos[1] >= window_y):
            game_over(player_score, ai_score, ai_crashed=True)

        # Draw everything
        game_window.fill(black)
        for block in player_body:
            pygame.draw.rect(game_window, green, pygame.Rect(block[0], block[1], 10, 10))
        for block in ai_body:
            pygame.draw.rect(game_window, blue, pygame.Rect(block[0], block[1], 10, 10))
        pygame.draw.rect(game_window, white, pygame.Rect(fruit_pos[0], fruit_pos[1], 10, 10))

        show_score(player_score, ai_score,label_left='Player', label_right='AI')
        show_countdown(remaining_time)
        pygame.display.update()
        fps.tick(snake_speed)
