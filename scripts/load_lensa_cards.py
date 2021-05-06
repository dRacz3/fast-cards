from src.cards.crud import add_multiple_new_white_card, add_multiple_new_black_card, add_new_deck
from src.cards.models import BlackCard, WhiteCard, DeckMetaData
from src.database.database import SessionLocal

LENSA = 'LENSA'

def bc(text, pick):
    return BlackCard(text=text, pick=pick, icon=LENSA, deck=LENSA)

def wc(text):
    return WhiteCard(text=text, icon=LENSA, deck=LENSA)

lensa_deck = {
    "name": LENSA,
    "white_cards": [
        wc(t)
        for t in [
            "Egy jó jobrec story",
            "The almighty SCRUM master",
            "újraírijukTM",
            "úgyiskidobjukTM",
            "Daily előtt egy percel frissíteni a boardot",
            "Daily alatt frissíteni a jira boardot",
            "A scrum master boldog",
            "A scrum master szomorú",
            "Egy jó elasticsearch verzióemelés vasárnap délután a crawlerek alatt",
            "Elfogy a sör az irodában",
            "Irodai ingyen ebéd",
            "Reggeli jóga az irodában",
            "Jó mint a WiFi a New Yorkban",
            "Megkérdezni az oroszlánt, hogy lekerülhetünk-e a halál listáról",
            "Pingpongozni Miamiban",
            "Palit nyaggatni a review-kal",
            "Délután megrohamozni a maradék kaját mielőtt elviszik",
            "Az előző sprint",
            "jobrec",
            "match",
            "preprocess",
            "job-enricher",
            "job-crawlerek",
            "Syndicated db takarítás"
        ]
    ],
    "black_cards": [
        bc("A jira board frissítése olyan, mint _", 1),
        bc("Amikor nincs assignee a sub-tasknál, akkor _", 1),
        bc("Szeretem a sprint célt, mint _-t", 1),
        bc("Szerintem a következő sprint cél legyen: _", 1),
        bc("Egypt has pyramids; we have _ ", 1),
        bc("The secret weapon in the war against bad sprints is _ ", 1),
    ],
}


if __name__ == "__main__":
    database = SessionLocal()
    add_new_deck(
        database,
        DeckMetaData(id_name=LENSA,
                     description='LENSA related terms in hungarian',
                     official=False,
                     name=LENSA,
                     icon=LENSA)
    )
    add_multiple_new_white_card(database, lensa_deck["white_cards"])
    add_multiple_new_black_card(database, lensa_deck["black_cards"])