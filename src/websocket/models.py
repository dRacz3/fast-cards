import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from fastapi.websockets import WebSocket
from starlette import status

from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)


@dataclass
class Room:
    room_name: str
    host_user: str
    connections: Dict[str, List[WebSocket]] = field(default_factory=dict)
    game_state_machine: Optional[GameStateMachine] = None

    @property
    def logger(self):
        return logging.getLogger(f"room-[{self.room_name}]")

    def add_user_to_room(self, user: str, connection: WebSocket):
        self.logger.info(f"Trying to add user {user} to room")
        if user not in self.connections.keys():
            self.connections[user] = []
        self.connections[user].append(connection)
        self.logger.info(f"Added user {user} to room")

    async def remove_user_from_room(self, user: str, connection: WebSocket):
        self.logger.info(f"Removed connection for user : {user} from room")
        try:
            await connection.close(code=status.WS_1001_GOING_AWAY)
        except Exception as e:
            self.logger.error(
                f"{e} => Connection seems to be already closed. Maybe a user connected multiple times?"
            )
        self.connections[user].remove(connection)
        if len(self.connections[user]) == 0:
            self.logger.info(
                f"No more user connections for this room {self.room_name} for user {user}, removing the user from room"
            )
            del self.connections[user]


@dataclass
class WebSocketMessage:
    message: str
    sender: str
    topic: str
