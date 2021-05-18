from src.cards.crud import add_multiple_new_white_card, add_multiple_new_black_card, add_new_deck
from src.cards.models import BlackCard, WhiteCard, DeckMetaData
from src.database.database import SessionLocal

VelocityRaptors = 'VelocityRaptors'

def bc(text, pick):
    return BlackCard(text=text, pick=pick, icon=VelocityRaptors, deck=VelocityRaptors)

def wc(text):
    return WhiteCard(text=text, icon=VelocityRaptors, deck=VelocityRaptors)

deck = {
    "name": VelocityRaptors,
    "white_cards": [
        wc(t)
        for t in [
          "Majd lesz hozzá design",
          "lensa site ",
          "Irodai ebéd ",
          "Délután megrohamozni a maradék kaját mielőtt elviszik",
          "Ingyen sör ",
          "Demo környezetek rendberakása ",
          "Nem bug, hanem feature ",
          "Gin tonic",
          "Megesküdni, hogy chromeban jól működik a fejlesztés ",
          "Semmi",
          "'Férfi mosdóban csereljünk kéztörlőt' onboarding",
          "Narancspusztító ",
          "“Prefer Testing Public APIs Over Implementation-Detail Classes” cikk",
          "Moderation page ",
          "Mobilapp ",
          "A/B teszt eredmények ",
          "JIRA bug ",
          "passzív-asszertív ",
          "Vetítés stand up alatt ",
          "Oltás utáni mellékhatás",
          "Stand up kezdés Ádám által",
        ]
    ],
    "black_cards": [
        bc('Bubu kifogása a fogorvossal szemben: _. ', 1),
        bc('A csapatépítő legjobb pillanata _ volt.', 1),
        bc('JIRA-t frissíteni olyan, mint _. Jó ha kész van, de senki se szereti csinálni  ', 1),
        bc('A megfelelő story point alapja _  ', 1),
        bc('Kis szél is tud nagy _-t csinálni', 1),
        bc('Gyorsasági KEG csere alatt ezt gondolom: _.', 1),
        bc('_-ra/re gondol Kozsó, amikor ezeket a sorokat énekli: Ihn nikho! Mahna nikho mha nahna e rei! Mha nahno mha nah rikho! Ihni Kohei!', 1),
        bc('Passzív agresszív kommunikáció az, amikor nem azt kaptad amit rendeltél, megetted, majd azt mondod a pincérnek, hogy _!', 1),
        bc('A munkatársak elismerése fontos számomra, ezért sokszor mondom nekik, hogy _. ', 1),
        bc('A chill roomba belépni tilos _ miatt! ', 1),
        bc('Szeretjük, mikor demo végén Andris azt mondja nekünk, hogy: ez a demo olyan volt, mint _.', 1),
        bc('_ volt a legérdekesebb dolog, amit Ati is Ádám tesztelés során talált.', 1),
        bc('Ha el kellene ülni a mostani helyünkről, akkor olyanok lennénk, mint _.', 1),
    ],
}


if __name__ == "__main__":
    database = SessionLocal()
    add_new_deck(
        database,
        DeckMetaData(id_name=VelocityRaptors,
                     description='VelocityRaptors related terms in hungarian',
                     official=False,
                     name=VelocityRaptors,
                     icon=VelocityRaptors)
    )
    add_multiple_new_white_card(database, deck["white_cards"])
    add_multiple_new_black_card(database, deck["black_cards"])
