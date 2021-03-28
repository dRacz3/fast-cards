from typing import List

import pytest
from fastapi.testclient import TestClient
from starlette import status

from src.cards.models import WhiteCard
from src.internal.cards_against_humanity_rules.game_event_processor import (
    GameEventProcessor,
)
from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    InvalidPlayerAction,
)
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStatePlayerView,
)
from src.internal.cards_against_humanity_rules.models import (
    CardsAgainstHumanityRoles,
    GameStates,
    SelectWinningSubmission,
    Submission,
)
from src.routers.game import GameEndpoints
from tests.conftest import default_header_with_token


class GameTestClient:
    def __init__(self, token, test_client: TestClient, room_name):
        self.test_client: TestClient = test_client
        self.header = default_header_with_token(token)
        self.room_name = room_name

    def start_game(self):
        return self.test_client.post(
            f"/game/{GameEndpoints.START_GAME}?room_name={self.room_name}",
            headers=self.header,
        )

    def new_game(self):
        return self.test_client.post(
            f"/game/{GameEndpoints.NEW}?room_name={self.room_name}", headers=self.header
        )

    def player_join(self):
        return self.test_client.post(
            f"/game/{GameEndpoints.JOIN}?room_name={self.room_name}",
            headers=self.header,
        )

    def refresh(self):
        return self.test_client.get(
            f"/game/{GameEndpoints.REFRESH}?room_name={self.room_name}",
            headers=self.header,
        )

    def submit(self, card_list: List[WhiteCard]):
        return self.test_client.post(
            f"/game/{GameEndpoints.SUBMIT}?room_name={self.room_name}",
            headers=self.header,
            json=[c.dict() for c in card_list],
        )

    def select_winner(self, winner: SelectWinningSubmission):
        return self.test_client.post(
            f"/game/{GameEndpoints.SELECTWINNER}?room_name={self.room_name}",
            headers=self.header,
            json=winner.dict(),
        )


@pytest.fixture()
def basic_game_setup_with_3_players(
    valid_user_token, test_client, get_clean_game_mapper, prefill_cards_to_database
):
    def _game_and_clients():
        prefill_cards_to_database()
        mapper = get_clean_game_mapper
        room_name = "test_room"
        client1 = GameTestClient(
            valid_user_token("user1"), test_client, room_name=room_name
        )
        client2 = GameTestClient(
            valid_user_token("user2"), test_client, room_name=room_name
        )
        client3 = GameTestClient(
            valid_user_token("user3"), test_client, room_name=room_name
        )

        new_game_response = client1.new_game()

        assert new_game_response.status_code == status.HTTP_200_OK
        assert client1.player_join().status_code == status.HTTP_200_OK
        assert client2.player_join().status_code == status.HTTP_200_OK
        assert client3.player_join().status_code == status.HTTP_200_OK
        assert mapper.get_game(room_name) is not None

        start_response = client1.start_game()
        assert start_response.status_code == status.HTTP_200_OK, start_response.content
        assert (
            GameStatePlayerView(**start_response.json()).state
            == GameStates.PLAYERS_SUBMITTING_CARDS
        )
        return mapper.get_game(room_name), client1, client2, client3

    yield _game_and_clients


def test_game_does_not_start_without_enough_players(
    valid_user_token, test_client, get_clean_game_mapper, prefill_cards_to_database
):
    prefill_cards_to_database()
    mapper = get_clean_game_mapper
    room_name = "test_room"
    client1 = GameTestClient(valid_user_token("user1"), test_client, room_name)
    new_game_response = client1.new_game()

    assert new_game_response.status_code == status.HTTP_200_OK
    assert client1.player_join().status_code == status.HTTP_200_OK
    assert mapper.get_game(room_name) is not None

    with pytest.raises(InvalidPlayerAction):
        start_response = client1.start_game()
        assert start_response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_game_creation(valid_user_token, test_client, get_clean_game_mapper, prefill_cards_to_database):
    prefill_cards_to_database()
    mapper = get_clean_game_mapper
    room_name = "test_room"
    client1 = GameTestClient(valid_user_token("user1"), test_client, room_name)
    client2 = GameTestClient(valid_user_token("user2"), test_client, room_name)

    new_game_response = client1.new_game()

    assert new_game_response.status_code == status.HTTP_200_OK
    assert client1.player_join().status_code == status.HTTP_200_OK
    assert client2.player_join().status_code == status.HTTP_200_OK
    assert mapper.get_game(room_name) is not None

    start_response = client1.start_game()
    assert start_response.status_code == status.HTTP_200_OK, start_response.content


def test_game_creation_fails_with_duplicate_name(valid_user_token, test_client, prefill_cards_to_database):
    prefill_cards_to_database()
    client1 = GameTestClient(valid_user_token("user1"), test_client, "test1")
    assert client1.new_game().status_code == status.HTTP_200_OK
    assert client1.new_game().status_code == status.HTTP_403_FORBIDDEN


def test_full_game(basic_game_setup_with_3_players):
    room, p1, p2, p3 = basic_game_setup_with_3_players()
    room: GameEventProcessor
    p1: GameTestClient
    p2: GameTestClient
    p3: GameTestClient

    assert len(room.session.players) == 3
    p1viewjson = p1.refresh().json()
    p1view = GameStatePlayerView(**p1viewjson)
    p2view = GameStatePlayerView(**p2.refresh().json())
    p3view = GameStatePlayerView(**p3.refresh().json())

    view_client = {
        p1view: p1,
        p2view: p2,
        p3view: p3,
    }

    client_view = {
        p1: p1view,
        p2: p2view,
        p3: p3view,
    }

    tzar = [
        p
        for p in [p1view, p2view, p3view]
        if p.player.current_role == CardsAgainstHumanityRoles.TZAR
    ][0]
    tzar_client = view_client[tzar]
    player_clients: List[GameTestClient] = [p1, p2, p3]
    player_clients.remove(tzar_client)
    for pc in player_clients:
        pc: GameTestClient
        view: GameStatePlayerView = client_view[pc]
        pc.submit(view.player.cards_in_hand[0 : view.currently_active_card.pick])

    tzar_view_after_submission = GameStatePlayerView(**tzar_client.refresh().json())

    assert tzar_view_after_submission.state == GameStates.TZAR_CHOOSING_WINNER

    winner_name = list(tzar_view_after_submission.player_submissions.keys())[0]
    tzar_client.select_winner(
        SelectWinningSubmission(
            submission=Submission(
                **tzar_view_after_submission.player_submissions[winner_name].dict()
            )
        )
    )

    view_after_winner_select = GameStatePlayerView(**tzar_client.refresh().json())
    assert view_after_winner_select.state == GameStates.PLAYERS_SUBMITTING_CARDS
    assert (
        view_after_winner_select.player.current_role != CardsAgainstHumanityRoles.TZAR
    ), "Same player cannot be a tzar again."
