from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio

# Import the puzzle generation and solving functions
from puzzle import generate_puzzle
from solver import solve_sudoku

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.game_rooms: Dict[int, List[int]] = {}  # Stores pairs of players in a game
        self.waiting_players: List[int] = []  # Stores players waiting to be paired
        self.game_states: Dict[
            int, Dict[str, List[List[int]]]
        ] = {}  # Stores the state of the games

    async def reset_game_state(self, room_id: int):
        # Reset the game state logic
        if room_id in self.game_states:
            del self.game_states[room_id]
        if room_id in self.game_rooms:
            for client_id in self.game_rooms[room_id]:
                await self.send_personal_message(
                    json.dumps({"action": "reset_game"}), client_id
                )
            del self.game_rooms[room_id]

    async def connect(self, client_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        if self.waiting_players:
            opponent_id = self.waiting_players.pop()
            room_id = min(client_id, opponent_id)
            self.game_rooms[room_id] = [client_id, opponent_id]
            await self.start_game(room_id)
        else:
            self.waiting_players.append(client_id)

    def disconnect(self, client_id: int):
        self.active_connections.pop(client_id, None)
        for room_id, players in self.game_rooms.items():
            if client_id in players:
                # Notify the other player that their opponent has left
                opponent_id = next(player for player in players if player != client_id)
                asyncio.create_task(
                    self.send_personal_message(
                        json.dumps({"action": "opponent_left"}), opponent_id
                    )
                )
                self.game_rooms.pop(room_id)
                self.game_states.pop(room_id, None)  # Clean up the game state
                break

    async def send_personal_message(self, message: str, client_id: int):
        websocket = self.active_connections.get(client_id)
        if websocket:
            await websocket.send_text(message)

    async def send_game_message(self, message: str, room_id: int):
        for client_id in self.game_rooms[room_id]:
            await self.send_personal_message(message, client_id)

    async def start_game(self, room_id: int):
        puzzle = generate_puzzle()
        solution = [[puzzle[i][j] for j in range(4)] for i in range(4)]
        solve_sudoku(solution)
        self.game_states[room_id] = {
            "puzzle": puzzle,
            "solution": solution,
        }  # Store the game state
        game_state = {
            "action": "start_game",
            "puzzle": puzzle,
            "room_id": room_id,  # Send room_id to clients
        }
        await self.send_game_message(json.dumps(game_state), room_id)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            action = data_json["action"]

            if action == "quick_pair":
                # If a client is waiting, pair them up, otherwise, add to waiting list
                if manager.waiting_players:
                    opponent_id = manager.waiting_players.pop(0)
                    room_id = min(client_id, opponent_id)
                    manager.game_rooms[room_id] = [client_id, opponent_id]
                    await manager.start_game(room_id)
                else:
                    manager.waiting_players.append(client_id)

            elif action == "submit_solution":
                room_id = data_json.get("room_id")
                if room_id is None or room_id not in manager.game_rooms:
                    await websocket.send_text(
                        json.dumps({"action": "error", "details": "Invalid room ID"})
                    )
                    continue

                solution = data_json["solution"]
                if validate_solution(solution, room_id):
                    await manager.send_game_message(
                        json.dumps({"action": "game_end", "winner": client_id}), room_id
                    )
                    await asyncio.sleep(1)  # Give clients time to process the end game message
                    await manager.reset_game_state(room_id)
                else:
                    # Notify the client their solution is incorrect
                    await manager.send_personal_message(
                        json.dumps({"action": "incorrect_solution"}), client_id
                    )
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        # Consider if you need to call reset_game_state when a disconnect happens
        # For example, if the client was in a game, you might want to reset that game's state
        # manager.reset_game_state(room_id)


# Additional endpoints for game logic would go here.


def validate_solution(submitted_solution, room_id):
    # Retrieve the correct solution stored in game_states
    correct_solution = manager.game_states.get(room_id, {}).get("solution", [])
    if not correct_solution:  # Check if the solution exists
        return False
    for i in range(4):
        for j in range(4):
            if submitted_solution[i][j] != correct_solution[i][j]:
                return False
    return True
