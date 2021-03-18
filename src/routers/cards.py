import json
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import src.cards.sql_models
import src.cards.crud
import src.cards.models

from src.dependencies import get_db, get_token_header

router = APIRouter(
    prefix="/cards",
    dependencies=[Depends(get_db)],
    tags=["cards"],
)


@router.post("/", response_model=src.cards.models.WhiteCard)
def create_card(card: src.cards.models.WhiteCard, db: Session = Depends(get_db)):
    _ = src.cards.crud.add_new_white_card(db, card)
    return card
