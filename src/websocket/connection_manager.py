from dataclasses import asdict
from typing import Optional, Dict

from fastapi import Cookie, Query, WebSocket, status

from src.websocket.models import Room, WebSocketMessage


class SENDER_TYPES:
    BROADCAST = "BROADCAST"
    PERSONAL = "DIRECT"


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Optional[str] = Cookie(None),
    token: Optional[str] = Query(None),
):
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


class ConnectionManager:
    def __init__(self):
        self.active_rooms: Dict[str, Room] = {}

    async def connect(self, room_name: str, username: str, websocket: WebSocket):
        room = self.active_rooms.get(room_name)
        if room is None:
            self.active_rooms[room_name] = Room(room_name=room_name, host_user=username)
            room = self.active_rooms[room_name]
        await websocket.accept()
        room.add_user_to_room(username, websocket)
        await self.broadcast(
            room_name,
            WebSocketMessage(
                message=f"{username} has entered room {room_name}",
                sender=SENDER_TYPES.BROADCAST,
                topic=room_name,
            ),
        )

    async def disconnect(self, room_name: str, username: str, websocket: WebSocket):
        await self.active_rooms[room_name].remove_user_from_room(username, websocket)

    async def send_personal_message(
        self, room_name: str, username: str, message: WebSocketMessage
    ):
        for connection in self.active_rooms[room_name].connections[username]:
            await connection.send_json(asdict(message))

    async def broadcast(self, room_name: str, message: WebSocketMessage):
        for connection_list in self.active_rooms[room_name].connections.values():
            for connection in connection_list:
                try:
                    await connection.send_json(asdict(message))
                except Exception as e:
                    print(
                        f"Could not send message -> {e}. Probalby connection was closed in the meantime."
                    )
