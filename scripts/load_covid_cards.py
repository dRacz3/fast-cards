from src.cards.crud import add_multiple_new_white_card, add_multiple_new_black_card, add_new_deck
from src.cards.models import BlackCard, WhiteCard, DeckMetaData
from src.database.database import SessionLocal


def bc(text, pick):
    return BlackCard(text=text, pick=pick, icon="COVID19", deck="COVID19")

def wc(text):
    return WhiteCard(text=text, icon="COVID19", deck="COVID19")

covid19 = {
    "name": "COVID19",
    "white_cards": [
        wc(t)
        for t in [
            "COVID19",
            "Oltástagadók",
            "Vakcina",
            "Vakcinairígység",
            "Vakcinaigazolvány",
            "3. hullám",
            "Müller cecília",
            "Nyunyóka",
            "Operatív Törzs",
            "Kínai vakcina",
            "Pfizer",
            "Brit-vérrög",
            "Astra-zeneca",
            "Járvány",
            "Oltásellennes balliberális ellenzék",
            "Azt gondolom, hogy valahol a küszöbön vagyunk jelenleg.",
            "Karantén",
            "Lélegeztetőgépek 20x áron",
            "Vírusos denevérpörkölt",
            "Maradjanak otthon",
            "Random Győrfi Pál",
            "Maradjanak otthon!"
        ]
    ],
    "black_cards": [
        bc("Azért tört ki a járvány mert _", 1),
        bc("Terraces open! _ allowed!", 1),
        bc(
            "A nyitás után a deákon _",
            1,
        ),
        bc("Azért nem kaptam még vakcinát mert _ ", 1),
        bc("_ is kialakultak a terasznyitás első etéjén", 1),
        bc("Elhunyt _, alapbetegsége: _ ", 2),
        bc("Csak az keresse fel orvosát aki _!", 1),
        bc("Ki merem jelenteni mára az is meggyógyult, aki _.", 1),
        bc("A koronavírus járvány a _-ig fog tartani.", 1),
        bc("Az oltás beadása után _", 1)
    ],
}


if __name__ == "__main__":
    database = SessionLocal()
    add_new_deck(
        database,
        DeckMetaData(id_name='COVID19',
                     description='covid 19 related terms in hungarian',
                     official=False,
                     name='COVID19',
                     icon='COVID19')
    )
    add_multiple_new_white_card(database, covid19["white_cards"])
    add_multiple_new_black_card(database, covid19["black_cards"])
