from fastapi import Depends, WebSocket, APIRouter
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from src.auth.auth_handler import decodeJWT
from src.dependencies import get_db, get_websocket_connection_manager
from src.users.crud import get_user_by_username
from src.websocket.models import WebSocketMessage
from src.websocket.connection_manager import ConnectionManager, SENDER_TYPES

router = APIRouter(
    prefix="/ws",
    tags=["ws"],
)


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
    username = decoded_content.user_id
    username = get_user_by_username(db, username).username
    await manager.connect(websocket=websocket, room_name=room_name, username=username)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(
            #     room_name,
            #     username,
            #     WebSocketMessage(
            #         message=f"You wrote: {data}",
            #         sender=SENDER_TYPES.PERSONAL,
            #         topic=room_name,
            #     ),
            # )
            await manager.broadcast(
                room_name,
                WebSocketMessage(
                    message=f"[{username}] {data}",
                    sender=SENDER_TYPES.SYSTEM,
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
                message=f"[{username}] disconnected",
                sender=SENDER_TYPES.SYSTEM,
                topic=room_name,
            ),
        )
