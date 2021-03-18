import json

from src.cards.crud import add_new_white_card, add_new_black_card
from src.cards.models import WhiteCard, BlackCard
from src.database.database import SessionLocal

with open("resources/hungarian_cards.json") as f:
    data = json.load(f)

db = SessionLocal()

print("Inserting white cards")
suc = 0
fail = 0
for i, key in enumerate(data["white"]):
    try:
        add_new_white_card(db, WhiteCard(card_id=1900 + i, **key))
        suc += 1
    except Exception as e:
        print(e)
        db.rollback()
        fail += 1

print(f"success:{suc},  failure: {fail}")


print("Inserting black cards")
suc = 0
fail = 0
for i, key in enumerate(data["black"]):
    try:
        add_new_black_card(db, BlackCard(card_id=i, **key))
        suc +=1
    except Exception as e:
        print(e)
        db.rollback()
        fail +=1

print(f"success:{ suc},  failure: {fail}")


