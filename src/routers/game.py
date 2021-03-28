from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth.auth_handler import decodeJWT
from src.cards.models import WhiteCard
from src.dependencies import get_game_mapper, get_websocket_connection_manager

from src.auth.auth_bearer import JWTBearer
from src.dependencies import get_db
from src.internal.cards_against_humanity_rules.game_event_processor import (
    GameEventMapper,
)
from src.internal.cards_against_humanity_rules.game_related_exceptions import GameHasEnded
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
    GameStatePlayerView,
)
from src.internal.cards_against_humanity_rules.models import (
    PlayerSubmitCards,
    SelectWinningSubmission,
)
from src.websocket.connection_manager import ConnectionManager, SENDER_TYPES
from src.websocket.models import WebSocketMessage

router = APIRouter(
    prefix="/game",
    dependencies=[Depends(get_db), Depends(JWTBearer())],
    tags=["cards-against"],
)


async def broadcast_event(
    room_name: str, connection_manager: ConnectionManager, message: str
):
    print(f"Broadcast attemt for : {room_name}->{message}")
    if connection_manager.active_rooms.get(room_name) is not None:
        await connection_manager.broadcast(
            room_name=room_name,
            message=WebSocketMessage(
                message=message, sender=SENDER_TYPES.SYSTEM, topic=room_name
            ),
        )
        print(f"BROADCASTED {room_name}->{message}")


class GameEndpoints:
    NEW = "new"
    JOIN = "join"
    START_GAME = "start_game"
    SUBMIT = "submit"
    SELECTWINNER = "selectwinner"
    LEAVE = "leave"
    REFRESH = "refresh"


class LeaveResponse(BaseModel):
    pass


@router.post(f"/{GameEndpoints.NEW}", response_model=GameStateMachine)
def create_new_game(
    room_name: str,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    db: Session = Depends(get_db),
):
    if game_mapper.get_game(room_name) is not None:
        raise HTTPException(403, "Room already exist.")
    return game_mapper.new_game(room_name, db).session.dict()


@router.post(f"/{GameEndpoints.JOIN}", response_model=GameStatePlayerView)
async def join_game(
    room_name: str,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
    conman: ConnectionManager = Depends(get_websocket_connection_manager),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")

    room.session.player_join(user.user_id)

    await broadcast_event(room_name, conman, f"{user.user_id} has joined the game!")

    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.post(f"/{GameEndpoints.LEAVE}", response_model=LeaveResponse)
async def leave_game(
    room_name: str,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
    conman: ConnectionManager = Depends(get_websocket_connection_manager),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")

    room.session.player_leaves(user.user_id)
    if len(room.session.players) == 0:
        game_mapper.end_game(room_name)

    await broadcast_event(room_name, conman, f"{user.user_id} has left the game!")

    return LeaveResponse()


@router.post(f"/{GameEndpoints.SUBMIT}", response_model=GameStatePlayerView)
async def submit_cards(
    room_name: str,
    cards: List[WhiteCard],
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
    conman: ConnectionManager = Depends(get_websocket_connection_manager),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")

    room.on_new_event(
        PlayerSubmitCards(submitting_user=user.user_id, cards=cards),
        user.user_id,
    )

    await broadcast_event(room_name, conman, f"{user.user_id} has submitted cards!")

    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.post(f"/{GameEndpoints.SELECTWINNER}", response_model=GameStatePlayerView)
async def select_winner(
    room_name: str,
    winner: SelectWinningSubmission,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
    conman: ConnectionManager = Depends(get_websocket_connection_manager),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")

    try:
        room.on_new_event(winner, user.user_id)
    except GameHasEnded as e:
        pass # It's fine. Just proceed.
    await broadcast_event(
        room_name, conman, f"{user.user_id} selected the winner, it is : {room.session.last_winner.username}"
    )

    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.post(f"/{GameEndpoints.START_GAME}", response_model=GameStatePlayerView)
async def start_game(
    room_name: str,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
    conman: ConnectionManager = Depends(get_websocket_connection_manager),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")

    room.session.start_game()

    await broadcast_event(
        room_name,
        conman,
        f"{user.user_id} has pressed start on the game! Buckle up, and enjoy",
    )

    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.get(f"/{GameEndpoints.REFRESH}", response_model=GameStatePlayerView)
def refresh(
    room_name: str,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")
    return GameStatePlayerView.from_game_state(room.session, user.user_id)


class Room(BaseModel):
    room_name: str
    player_count: int


class RoomListing(BaseModel):
    rooms: List[Room]


@router.get(f"/rooms", response_model=RoomListing)
def list_rooms(game_mapper: GameEventMapper = Depends(get_game_mapper)):
    room = [g.session for g in game_mapper.mapping.values()]
    return RoomListing(
        rooms=[Room(room_name=r.room_name, player_count=len(r.players)) for r in room]
    )
