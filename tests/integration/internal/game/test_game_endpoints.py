import pytest
from fastapi.testclient import TestClient
from starlette import status

from src.internal.cards_against_humanity_rules.game_related_exceptions import InvalidPlayerAction
from src.routers.game import GameEndpoints
from tests.conftest import default_header_with_token

class GameTestClient():
    def __init__(self, token, test_client : TestClient):
        self.test_client : TestClient = test_client
        self.header = default_header_with_token(token)

    def start_game(self, room_name):
        return self.test_client.post(f"/game/{GameEndpoints.START_GAME}?room_name={room_name}",
                                     headers = self.header
                                     )

    def new_game(self, room_name):
        return self.test_client.post(f"/game/{GameEndpoints.NEW}?room_name={room_name}",
                                     headers=self.header
                                     )

    def player_join(self, room_name):
        return self.test_client.post(f"/game/{GameEndpoints.JOIN}?room_name={room_name}",
                                     headers=self.header
                                     )


def test_game_does_not_start_without_enough_players(valid_user_token, test_client, get_clean_game_mapper):
    mapper = get_clean_game_mapper
    client1 = GameTestClient(valid_user_token("user1"), test_client)
    room_name = "test_room"
    new_game_response = client1.new_game(room_name)

    assert new_game_response.status_code == status.HTTP_200_OK
    assert client1.player_join(room_name).status_code == status.HTTP_200_OK
    assert mapper.get_game(room_name) is not None

    with pytest.raises(InvalidPlayerAction):
        start_response = client1.start_game(room_name)
        assert start_response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR



def test_game_creation(valid_user_token, test_client, get_clean_game_mapper):
    mapper = get_clean_game_mapper
    client1 = GameTestClient(valid_user_token("user1"), test_client)
    client2 = GameTestClient(valid_user_token("user2"), test_client)
    room_name = "test_room"
    new_game_response = client1.new_game(room_name)

    assert new_game_response.status_code == status.HTTP_200_OK
    assert client1.player_join(room_name).status_code == status.HTTP_200_OK
    assert client2.player_join(room_name).status_code == status.HTTP_200_OK
    assert mapper.get_game(room_name) is not None

    start_response = client1.start_game(room_name)
    assert start_response.status_code == status.HTTP_200_OK, start_response.content