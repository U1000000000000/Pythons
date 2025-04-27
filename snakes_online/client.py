import pygame
import asyncio
import threading
import websockets
import json

WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20

player_snake = []
other_snake = []
food = [100, 100]
direction = "RIGHT"
websocket = None
network_loop = None
player_id = None
room_id = None
game_state = "menu"  # menu, waiting, playing

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

async def connect_to_server():
    global websocket, player_snake, other_snake, food, player_id, room_id, game_state

    async with websockets.connect("ws://localhost:6789") as ws:
        websocket = ws
        while True:
            try:
                msg = await websocket.recv()
                data = json.loads(msg)

                if data["type"] == "room_created":
                    room_id = data["room_id"]
                    player_id = data["player_id"]
                    game_state = "waiting"
                    player_snake = [[100, 100]]  # Initialize player snake
                    other_snake = []  # Initialize empty other snake

                elif data["type"] == "game_started":
                    room_id = data["room_id"]
                    player_id = data["player_id"]
                    game_state = "playing"

                elif data["type"] == "state":
                    if "game_started" in data and data["game_started"]:
                        game_state = "playing"

                    if player_id is not None:
                        # Update both snakes
                        for player in data["players"]:
                            if player["id"] == player_id:
                                player_snake = player["snake"]
                            else:
                                other_snake = player["snake"]
                        food = data["food"]

                elif data["type"] == "error":
                    print(f"Error: {data['message']}")

            except websockets.ConnectionClosed:
                print("Connection closed")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

def start_network_thread():
    global network_loop
    network_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(network_loop)
    network_loop.run_until_complete(connect_to_server())

async def send_create_room():
    if websocket:
        await websocket.send(json.dumps({"type": "create"}))

async def send_join_room(room_id_to_join):
    if websocket:
        await websocket.send(json.dumps({
            "type": "join",
            "room_id": room_id_to_join
        }))

async def send_input(direction):
    if websocket and room_id is not None and player_id is not None:
        await websocket.send(json.dumps({
            "type": "input",
            "dir": direction,
            "room_id": room_id,
            "player_id": player_id
        }))

def draw_menu(screen):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 36)

    title = font.render("Multiplayer Snake", True, WHITE)
    create_text = font.render("1. Create Room", True, WHITE)
    join_text = font.render("2. Join Room", True, WHITE)

    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    screen.blit(create_text, (WIDTH//2 - create_text.get_width()//2, 150))
    screen.blit(join_text, (WIDTH//2 - join_text.get_width()//2, 200))

    pygame.display.flip()

def draw_waiting(screen):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 36)

    waiting_text = font.render(f"Waiting for player in room {room_id}", True, WHITE)
    screen.blit(waiting_text, (WIDTH//2 - waiting_text.get_width()//2, HEIGHT//2))

    pygame.display.flip()

def draw_game(screen):
    screen.fill(BLACK)

    for part in player_snake:
        pygame.draw.rect(screen, GREEN, pygame.Rect(part[0], part[1], GRID_SIZE, GRID_SIZE))

    for part in other_snake:
        pygame.draw.rect(screen, BLUE, pygame.Rect(part[0], part[1], GRID_SIZE, GRID_SIZE))

    pygame.draw.rect(screen, RED, pygame.Rect(food[0], food[1], GRID_SIZE, GRID_SIZE))

    # Display room info
    font = pygame.font.SysFont(None, 24)
    room_text = font.render(f"Room: {room_id}", True, WHITE)
    screen.blit(room_text, (10, 10))

    pygame.display.flip()

def main():
    global direction, websocket, network_loop, game_state, room_id

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Multiplayer Snake")
    clock = pygame.time.Clock()

    # Start network thread
    threading.Thread(target=start_network_thread, daemon=True).start()

    input_active = False
    room_input = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if game_state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        # Create room
                        asyncio.run_coroutine_threadsafe(send_create_room(), network_loop)
                    elif event.key == pygame.K_2:
                        # Join room - activate input
                        input_active = True
                        room_input = ""

            elif game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        direction = "UP"
                    elif event.key == pygame.K_DOWN:
                        direction = "DOWN"
                    elif event.key == pygame.K_LEFT:
                        direction = "LEFT"
                    elif event.key == pygame.K_RIGHT:
                        direction = "RIGHT"

                    if websocket and network_loop:
                        asyncio.run_coroutine_threadsafe(send_input(direction), network_loop)

            # Handle room ID input
            if input_active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if room_input:
                        asyncio.run_coroutine_threadsafe(send_join_room(room_input), network_loop)
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    room_input = room_input[:-1]
                elif event.unicode.isdigit():
                    room_input += event.unicode

        # Drawing
        if game_state == "menu":
            draw_menu(screen)
            if input_active:
                font = pygame.font.SysFont(None, 36)
                input_text = font.render(f"Enter Room ID: {room_input}", True, WHITE)
                screen.blit(input_text, (WIDTH//2 - input_text.get_width()//2, 250))
                pygame.display.flip()
        elif game_state == "waiting":
            draw_waiting(screen)
        elif game_state == "playing":
            draw_game(screen)

        clock.tick(15)

if __name__ == "__main__":
    main()
