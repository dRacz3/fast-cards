from typing import Optional, List

from fastapi import Cookie, Depends, FastAPI, Query, WebSocket, status, APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from src.auth.auth_bearer import JWTBearer
from src.auth.auth_handler import decodeJWT
from src.auth.models import UserSchema
from src.dependencies import get_token_header, get_db
from src.users.crud import get_user_by_email
from src.websocket_pilot.models import Room

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
            var ws = new WebSocket(`ws://localhost:8000/ws/lobby/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWJkdWxhemVlekB4LmNvbSIsImV4cGlyZXMiOjE2MTYzMzQzMjEuMDMwMTAzfQ.oHmCk_TOB6oHYcZKOPG3gXh6JG5suQCnml-fXkovCok`);
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
    # dependencies=[Depends(get_db)],
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
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


# @router.websocket("/items/{item_id}/ws")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     item_id: str,
#     q: Optional[int] = None,
#     cookie_or_token: str = Depends(get_cookie_or_token),
# ):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(
#             f"Session cookie or query token value is: {cookie_or_token}"
#         )
#         if q is not None:
#             await websocket.send_text(f"Query parameter q is: {q}")
#         await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")


@router.websocket("/ws/{room_name}/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_name: str,
    token,
    db: Session = Depends(get_db)
):
    decoded_content = decodeJWT(token)
    if decoded_content is None:
        raise Exception("No valid credentials!")
    user_email = decoded_content.user_id
    username = get_user_by_email(db ,user_email).username
    Room.create_room(db, room_name=room_name, creator=username)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"[{username}] says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"[{username}] left the chat")
