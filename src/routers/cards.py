from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import src.cards.crud
import src.cards.models
from src.auth.auth_bearer import JWTBearer

from src.dependencies import get_db

router = APIRouter(
    prefix="/cards",
    dependencies=[Depends(get_db), Depends(JWTBearer())],
    tags=["cards"],
)

# TODO: add tests for source checking over endpoint
@router.put("/white", response_model=src.cards.models.WhiteCard)
def create_white_card(card: src.cards.models.WhiteCard, db: Session = Depends(get_db)):
    try:
        _ = src.cards.crud.add_new_white_card(db, card, source="user")
        return card
    except Exception as e:
        raise HTTPException(400, f"Failed to add card. {e}")


@router.put("/black", response_model=src.cards.models.BlackCard)
def create_black_card(card: src.cards.models.BlackCard, db: Session = Depends(get_db)):
    try:
        _ = src.cards.crud.add_new_black_card(db, card, source="user")
        return card
    except Exception as e:
        raise HTTPException(400, f"Failed to add card. {e}")


@router.put("/deck", response_model=src.cards.models.DeckMetaData)
def create_deck(deck: src.cards.models.DeckMetaData, db: Session = Depends(get_db)):
    try:
        _ = src.cards.crud.add_new_deck(db, deck, source="user")
        return deck
    except Exception as e:
        raise HTTPException(400, f"Failed to add deck. {e}")


# TODO : add test for it
@router.get("/deck", response_model=List[src.cards.models.DeckMetaData])
def get_deck_list(db: Session = Depends(get_db)):
    return src.cards.crud.get_deck_list(db)
