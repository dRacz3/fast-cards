from dataclasses import asdict
from typing import Optional, Dict

from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from src.auth.auth_handler import decodeJWT
from src.dependencies import get_db
from src.users.crud import get_user_by_email
from src.websocket_pilot.models import Room, WebSocketMessage

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/lobby/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJkdWxhemVlekB4LmNvbSIsImV4cGlyZXMiOjE2MTYzMzk3MTkuMDgzOTAzfQ.LTvJfpF62SndBq_tqPqAtj5IR5wlE75hMN34Vofn8C4`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)


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

    def disconnect(self, room_name: str, username: str, websocket: WebSocket):
        self.active_rooms[room_name].remove_user_from_room(username, websocket)

    async def send_personal_message(
        self, room_name : str,  username : str,message: WebSocketMessage
    ):
        for connection in self.active_rooms[room_name].connections[username]:
            await connection.send_json(asdict(message))

    async def broadcast(self, room_name: str, message: WebSocketMessage):
        for connection_list in self.active_rooms[room_name].connections.values():
            for connection in connection_list:
                await connection.send_json(asdict(message))


manager = ConnectionManager()


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws/{room_name}/{token}")
async def websocket_endpoint(
    websocket: WebSocket, room_name: str, token, db: Session = Depends(get_db)
):
    decoded_content = decodeJWT(token)
    if decoded_content is None:
        raise Exception("No valid credentials!")
    user_email = decoded_content.user_id
    username = get_user_by_email(db, user_email).username
    await manager.connect(websocket=websocket, room_name=room_name, username=username)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(
                room_name,
                username,
                WebSocketMessage(
                    message=f"You wrote: {data}",
                    sender="PERSONAL",
                    topic=room_name,
                ),
            )
            await manager.broadcast(
                room_name,
                WebSocketMessage(
                    message=f"[{username}] says: {data}",
                    sender="BROADCAST",
                    topic=room_name,
                ),
            )
    except WebSocketDisconnect:
        manager.disconnect(room_name=room_name, username=username, websocket=websocket)
        await manager.broadcast(
            room_name,
            WebSocketMessage(
                message=f"[{username}] left the chat",
                sender="BROADCAST",
                topic=room_name,
            ),
        )
