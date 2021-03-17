from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class DeckMetaData(BaseModel):
    id_name: str
    description: str
    official: bool = False
    name: str
    icon: str

    def __str__(self):
        return f"{self.id_name} - {self.name}"


class BlackCard(BaseModel):
    card_id: int
    text: str
    icon: str
    deck: str
    pick: int

    def __str__(self):
        return f"<{self.card_id}>[{self.deck}] {self.text}"


class WhiteCard(BaseModel):
    card_id: int
    text: str
    icon: str
    deck: str

    def __str__(self):
        return f"<{self.card_id}> [{self.deck}] {self.text}"
