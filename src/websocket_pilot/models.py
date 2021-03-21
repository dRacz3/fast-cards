from dataclasses import dataclass, field
from typing import List, Dict

from fastapi.websockets import WebSocket
from starlette import status

@dataclass
class Room:
    room_name: str
    host_user: str
    connections: Dict[str, List[WebSocket]] = field(default_factory=dict)

    def add_user_to_room(self, user: str, connection: WebSocket):
        print(f"Trying to add user {user} to room")
        if user not in self.connections.keys():
            self.connections[user] = []
        self.connections[user].append(connection)
        print(f"Added user {user} to room")

    def remove_user_from_room(self, user: str, connection: WebSocket):
        print(f"Removed connection for user : {user} from room")
        connection.close(code=status.WS_1001_GOING_AWAY)
        self.connections[user].remove(connection)
        if len(self.connections[user]) == 0:
            print(
                f"No more user connections for this room {self.room_name} for user {user}, removing the user from room"
            )
            del self.connections[user]
