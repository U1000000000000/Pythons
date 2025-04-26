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
network_loop = None  # ← Add this

# Connect to server in background and receive state updates
async def connect_to_server():
    global websocket, player_snake, other_snake, food

    async with websockets.connect("ws://localhost:6789") as ws:
        websocket = ws
        while True:
            try:
                msg = await websocket.recv()
                data = json.loads(msg)
                if data["type"] == "state":
                    players = data["players"]
                    if len(players) > 0:
                        player_snake = players[0]["snake"]
                        other_snake = players[1]["snake"] if len(players) > 1 else []
                        food = data["food"]
            except websockets.ConnectionClosed:
                print("Connection closed")
                break

# Thread wrapper for asyncio
def start_network_thread():
    global network_loop
    network_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(network_loop)
    network_loop.run_until_complete(connect_to_server())

# Main game loop (runs on main thread)
def draw_game():
    global direction, websocket

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Multiplayer Snake")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

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

        screen.fill((0, 0, 0))

        for part in player_snake:
            pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(part[0], part[1], GRID_SIZE, GRID_SIZE))

        for part in other_snake:
            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(part[0], part[1], GRID_SIZE, GRID_SIZE))

        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food[0], food[1], GRID_SIZE, GRID_SIZE))

        pygame.display.flip()
        clock.tick(15)

# Async send message
async def send_input(direction):
    try:
        await websocket.send(json.dumps({"type": "input", "dir": direction}))
    except Exception as e:
        print(f"Error sending input: {e}")

# Main
if __name__ == "__main__":
    threading.Thread(target=start_network_thread, daemon=True).start()
    draw_game()
