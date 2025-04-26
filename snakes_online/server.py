import asyncio
import websockets
import json
import random

GRID_SIZE = 20
WIDTH, HEIGHT = 600, 400
TICK_RATE = 0.2  # seconds

clients = []
players = []
food = [random.randrange(0, WIDTH, GRID_SIZE), random.randrange(0, HEIGHT, GRID_SIZE)]

def create_snake(start_x, start_y):
    return [[start_x, start_y]]

def get_new_position(pos, direction):
    x, y = pos
    if direction == "UP":
        return [x, y - GRID_SIZE]
    elif direction == "DOWN":
        return [x, y + GRID_SIZE]
    elif direction == "LEFT":
        return [x - GRID_SIZE, y]
    elif direction == "RIGHT":
        return [x + GRID_SIZE, y]
    return pos

def valid_direction_change(current, new):
    opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
    return new != opposites.get(current)

async def update_loop():
    global food
    while True:
        for p in players:
            head = p["snake"][0]
            new_head = get_new_position(head, p["dir"])
            p["snake"].insert(0, new_head)

            # Check if food eaten
            if new_head == food:
                food = [random.randrange(0, WIDTH, GRID_SIZE), random.randrange(0, HEIGHT, GRID_SIZE)]
            else:
                p["snake"].pop()  # Move forward

        # Broadcast state
        data = {"type": "state", "players": players, "food": food}
        for ws in clients:
            try:
                await ws.send(json.dumps(data))
            except:
                pass
        await asyncio.sleep(TICK_RATE)

async def handler(websocket):
    global clients

    if len(players) >= 2:
        await websocket.send(json.dumps({"type": "error", "message": "Game full!"}))
        await websocket.close()
        return

    clients.append(websocket)
    idx = len(players)
    start_pos = [[100, 100], [400, 300]][idx]
    players.append({
        "snake": create_snake(*start_pos),
        "dir": "RIGHT"
    })

    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "input":
                player = players[idx]
                new_dir = data["dir"]
                if valid_direction_change(player["dir"], new_dir):
                    player["dir"] = new_dir
    except:
        pass
    finally:
        clients.remove(websocket)
        if idx < len(players):
            players.pop(idx)

async def main():
    print("Server started on port 6789")
    await asyncio.gather(
        websockets.serve(handler, "localhost", 6789),
        update_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())
