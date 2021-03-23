from typing import List

from fastapi import APIRouter, HTTPException, Depends
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
    Submission,
)

router = APIRouter(
    prefix="/game",
    dependencies=[Depends(get_db), Depends(JWTBearer())],
    tags=["cards-against"],
)


@router.post("/new", response_model=GameStateMachine)
def create_new_game(
    room_name: str,
    game_mapper: GameEventMapper = Depends(get_game_mapper),
    db: Session = Depends(get_db),
):
    if game_mapper.get_game(room_name) is not None:
        raise HTTPException(403, "Room already exist.")
    return game_mapper.new_game(room_name, db).session.dict()


@router.post("/join", response_model=GameStatePlayerView)
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


@router.post("/leave")
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

    game_mapper.get_game(room_name).session.player_leaves(user.user_id)
    return 200, "OK"


@router.post("/submit", response_model=GameStatePlayerView)
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


@router.post("/selectwinner", response_model=GameStatePlayerView)
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


@router.post("/start_game", response_model=GameStatePlayerView)
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
