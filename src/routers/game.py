from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth.auth_handler import decodeJWT
from src.cards.models import WhiteCard
from src.dependencies import get_game_mapper

from src.auth.auth_bearer import JWTBearer
from src.dependencies import get_db
from src.internal.cards_against_humanity_rules.game_event_processor import (
    GameEventMapper,
)
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
    GameStatePlayerView,
)
from src.internal.cards_against_humanity_rules.models import (
    PlayerSubmitCards,
    SelectWinningSubmission,
)

router = APIRouter(
    prefix="/game",
    dependencies=[Depends(get_db), Depends(JWTBearer())],
    tags=["cards-against"],
)


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
def join_game(
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

    room.session.player_join(user.user_id)

    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.post(f"/{GameEndpoints.LEAVE}", response_model=LeaveResponse)
def leave_game(
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

    room.session.player_leaves(user.user_id)
    return LeaveResponse()


@router.post(f"/{GameEndpoints.SUBMIT}", response_model=GameStatePlayerView)
def submit_cards(
    room_name: str,
    cards: List[WhiteCard],
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
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
    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.post(f"/{GameEndpoints.SELECTWINNER}", response_model=GameStatePlayerView)
def select_winner(
    room_name: str,
    winner: SelectWinningSubmission,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    token: str = Depends(JWTBearer()),
):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    room = game_mapper.get_game(room_name)
    if room is None:
        raise HTTPException(404, "Room does not exist.")

    room.on_new_event(winner, user.user_id)
    return GameStatePlayerView.from_game_state(room.session, user.user_id)


@router.post(f"/{GameEndpoints.START_GAME}", response_model=GameStatePlayerView)
def start_game(
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

    room.session.start_game()
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
