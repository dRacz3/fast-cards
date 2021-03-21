from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import src.cards.crud
import src.cards.models
from src.auth.auth_bearer import JWTBearer
from src.auth.auth_handler import decodeJWT

from src.dependencies import get_db

router = APIRouter(
    prefix="/cards",
    dependencies=[Depends(get_db), Depends(JWTBearer())],
    tags=["cards"],
)


@router.put("/white", response_model=src.cards.models.WhiteCard)
def create_white_card(card: src.cards.models.WhiteCard, db: Session = Depends(get_db)):
    _ = src.cards.crud.add_new_white_card(db, card)
    return card


@router.put("/black", response_model=src.cards.models.BlackCard)
def create_black_card(card: src.cards.models.BlackCard, db: Session = Depends(get_db)):
    _ = src.cards.crud.add_new_black_card(db, card)
    return card
