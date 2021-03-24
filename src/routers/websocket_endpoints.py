from fastapi import Depends, WebSocket, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect

from src.auth.auth_handler import decodeJWT
from src.dependencies import get_db, get_websocket_connection_manager
from src.users.crud import get_user_by_email
from src.websocket.models import WebSocketMessage
from src.websocket.connection_manager import ConnectionManager, SENDER_TYPES

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

#
# @router.get("/",)
# async def get():
#     return HTMLResponse(html)
#

@router.websocket("/ws/{room_name}/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_name: str,
    token,
    db: Session = Depends(get_db),
    manager: ConnectionManager = Depends(get_websocket_connection_manager),
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
                    sender=SENDER_TYPES.PERSONAL,
                    topic=room_name,
                ),
            )
            await manager.broadcast(
                room_name,
                WebSocketMessage(
                    message=f"[{username}] says: {data}",
                    sender=SENDER_TYPES.BROADCAST,
                    topic=room_name,
                ),
            )
    except WebSocketDisconnect:
        await manager.disconnect(
            room_name=room_name, username=username, websocket=websocket
        )
        await manager.broadcast(
            room_name,
            WebSocketMessage(
                message=f"[{username}] left the chat",
                sender=SENDER_TYPES.BROADCAST,
                topic=room_name,
            ),
        )
