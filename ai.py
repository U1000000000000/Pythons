import random
from settings import *

def ai_snake_move(ai_position, ai_body, ai_direction, fruit_position, ai_difficulty):
    # Easy mode: 30% random
    if ai_difficulty == 'Easy' and random.random() < 0.3:
        ai_direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    elif ai_difficulty == 'Medium' and random.random() < 0.15:
        ai_direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT'])
    else:
        if ai_position[0] < fruit_position[0]: ai_direction = 'RIGHT'
        elif ai_position[0] > fruit_position[0]: ai_direction = 'LEFT'
        elif ai_position[1] < fruit_position[1]: ai_direction = 'DOWN'
        elif ai_position[1] > fruit_position[1]: ai_direction = 'UP'

    if ai_direction == 'UP': ai_position[1] -= 10
    elif ai_direction == 'DOWN': ai_position[1] += 10
    elif ai_direction == 'LEFT': ai_position[0] -= 10
    elif ai_direction == 'RIGHT': ai_position[0] += 10

    ai_body.insert(0, list(ai_position))
    return ai_direction, ai_position, ai_body
