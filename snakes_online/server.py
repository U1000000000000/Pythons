import asyncio
import websockets
import json
import random
from collections import defaultdict

GRID_SIZE = 20
WIDTH, HEIGHT = 600, 400
TICK_RATE = 0.2  # seconds

# Data structures to manage rooms
rooms = defaultdict(dict)  # room_id: {clients: [], players: [], food: []}
room_counter = 0

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

async def update_room(room_id):
    room = rooms[room_id]
    while room and len(room["clients"]) > 0:
        # Only update game state if game has started
        if room["game_started"]:
            for p in room["players"]:
                head = p["snake"][0]
                new_head = get_new_position(head, p["dir"])
                p["snake"].insert(0, new_head)

                # Check if food eaten
                if new_head == room["food"]:
                    room["food"] = [random.randrange(0, WIDTH, GRID_SIZE),
                                   random.randrange(0, HEIGHT, GRID_SIZE)]
                else:
                    p["snake"].pop()  # Move forward

        # Broadcast state to all clients in the room
        data = {
            "type": "state",
            "players": [{
                "id": p["id"],
                "snake": p["snake"],
                "dir": p["dir"]
            } for p in room["players"]],
            "food": room["food"],
            "room_id": room_id,
            "game_started": room["game_started"]  # Include game state
        }
        for ws in room["clients"]:
            try:
                await ws.send(json.dumps(data))
            except:
                pass
        await asyncio.sleep(TICK_RATE)

async def handler(websocket):
    global room_counter

    try:
        # First message should be either create or join
        message = await websocket.recv()
        data = json.loads(message)

        if data["type"] == "create":
            # Create new room
            room_id = str(room_counter)
            room_counter += 1
            rooms[room_id] = {
                "clients": [websocket],
                "players": [],
                "food": [random.randrange(0, WIDTH, GRID_SIZE),
                         random.randrange(0, HEIGHT, GRID_SIZE)],
                "game_started": False
            }
            # Add first player
            players = rooms[room_id]["players"]
            players.append({
                "snake": create_snake(100, 100),
                "dir": "RIGHT",
                "id": 0,
                "ws": websocket
            })
            # Start game loop for this room
            asyncio.create_task(update_room(room_id))
            # Send room created message (not game state yet)
            await websocket.send(json.dumps({
                "type": "room_created",
                "room_id": room_id,
                "player_id": 0
            }))

            # Keep connection alive for game inputs
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "input":
                    player = next((p for p in rooms[room_id]["players"] if p["id"] == 0), None)
                    if player and valid_direction_change(player["dir"], data["dir"]):
                        player["dir"] = data["dir"]

        elif data["type"] == "join":
            room_id = data["room_id"]
            if room_id not in rooms:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Room not found"
                }))
                await websocket.close()
                return

            room = rooms[room_id]
            if len(room["players"]) >= 2:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Room full"
                }))
                await websocket.close()
                return

            # Add client to room
            room["clients"].append(websocket)
            # Add player
            player_id = len(room["players"])
            start_positions = [[100, 100], [400, 300]]
            room["players"].append({
                "snake": create_snake(*start_positions[player_id]),
                "dir": "RIGHT",
                "id": player_id,
                "ws": websocket
            })

            # Mark game as started
            room["game_started"] = True

            # Notify both players that game has started
            for i, client in enumerate(room["clients"]):
                await client.send(json.dumps({
                    "type": "game_started",
                    "room_id": room_id,
                    "player_id": i
                }))

            # Keep connection alive for game inputs
            async for message in websocket:
                data = json.loads(message)
                if data["type"] == "input":
                    player = next((p for p in rooms[room_id]["players"] if p["id"] == player_id), None)
                    if player and valid_direction_change(player["dir"], data["dir"]):
                        player["dir"] = data["dir"]

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up - remove client from room
        for room_id, room in rooms.items():
            if websocket in room["clients"]:
                room["clients"].remove(websocket)
                # Remove player if exists
                player_id = next((i for i, p in enumerate(room["players"])
                                if p.get("ws") == websocket), None)
                if player_id is not None:
                    room["players"].pop(player_id)
                break

async def main():
    print("Server started on port 6789")
    async with websockets.serve(handler, "localhost", 6789):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
