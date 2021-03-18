from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import cards_server.cards.sql_models
import cards_server.cards.crud
import cards_server.cards.models

from cards_server.dependencies import get_db, get_token_header

router = APIRouter(
    prefix="/cards",
    dependencies=[Depends(get_db)],
    tags=["cards"],
)


@router.post("/", response_model=cards_server.cards.models.WhiteCard)
def create_card(card: cards_server.cards.models.WhiteCard, db: Session = Depends(get_db)):
    _ = cards_server.cards.crud.add_new_white_card(db, card)
    return card
