from typing import List

import pytest

from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    InvalidPlayerAction,
    LogicalError,
    GameHasEnded,
)
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)
from src.internal.cards_against_humanity_rules.models import (
    CARDS_IN_PLAYER_HAND,
    GameStates,
    CardsAgainstHumanityRoles,
    CardsAgainstHumanityPlayer,
    Submission,
    POINTS_TO_WIN,
    PlayerSubmitCards,
    SelectWinningSubmission,
)


@pytest.fixture()
def default_game_with_3_players(database_connection, prefill_cards_to_database):
    prefill_cards_to_database()
    db = database_connection
    sess = GameStateMachine.new_session("test", 5, db)
    ### STARTING GAME PHASE ######
    assert not sess.start_game()
    assert sess.state == GameStates.STARTING

    sess.player_join("Joe")
    sess.player_join("David")
    sess.player_join("Peter")
    yield sess


def test_game_session_creation_and_user_assignment(
    database_connection, prefill_cards_to_database
):
    prefill_cards_to_database()
    db = database_connection
    sess = GameStateMachine.new_session("test", 5, db)
    assert len(sess.players) == 0
    assert len(sess.black_cards) == 5
    assert len(sess.white_cards) > 15

    sess.player_join("Joe")
    sess.player_join("David")

    assert len(sess.players) == 2

    player_names = [p.username for p in sess.players]
    assert "Joe" in player_names
    assert "David" in player_names

    for p in sess.players:
        assert len(p.cards_in_hand) == CARDS_IN_PLAYER_HAND

    sess.player_leaves("David")
    assert len(sess.players) == 1
    player_names = [p.username for p in sess.players]
    assert "Joe" in player_names


def test_game_starts_only_with_enough_players(
    database_connection, prefill_cards_to_database
):
    prefill_cards_to_database()
    db = database_connection
    sess: GameStateMachine = GameStateMachine.new_session("test", 5, db)
    ### STARTING GAME PHASE ######
    assert not sess.start_game()
    assert sess.state == GameStates.STARTING

    sess.player_join("Joe")
    sess.player_join("David")
    sess.player_join("Peter")

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    assert sess.currently_active_card.pick is not None

    ### TZAR ELECTION ###
    tzars = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.TZAR
    ]
    assert len(tzars) == 1
    first_tzar = tzars[0]

    everyone_else: List[CardsAgainstHumanityPlayer] = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]

    ### ASSERTING PLAYER CARD ASSIGNMENT ###
    active_card_picks = sess.currently_active_card.pick
    for player in everyone_else:
        assert len(player.cards_in_hand) == CARDS_IN_PLAYER_HAND
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=player.username,
                cards=player.cards_in_hand[0:active_card_picks],
            )
        )
        assert len(player.cards_in_hand) == CARDS_IN_PLAYER_HAND - active_card_picks

    ### TZAR IS CHOSING THE WINNER ###
    assert sess.state == GameStates.TZAR_CHOOSING_WINNER
    the_winner_player: CardsAgainstHumanityPlayer = everyone_else[0]
    winning_submission = the_winner_player.submissions[-1]

    sess.select_winner(winning_submission)

    ### CHECK AWARDED POINTS ###
    for p in everyone_else:
        if p != the_winner_player:
            assert p.points == 0
        else:
            assert p.points == 1

    ### IMPLICITLY A NEW ROUND HAS STARTED ###
    new_tzars = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.TZAR
    ]
    assert len(new_tzars) == 1, "must be only 1 tzar!"
    assert (
        new_tzars[0] != first_tzar
    ), "The same player cannot be tzar two times in a row"


def test_invalid_player_action_when_player_tries_to_submit_cards(
    default_game_with_3_players,
):
    sess: GameStateMachine = default_game_with_3_players
    with pytest.raises(InvalidPlayerAction):
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=sess.players[0].username,
                cards=sess.players[0].cards_in_hand[0:1],
            )
        )


def test_invalid_player_action_when_player_tries_to_submit_cards_wrong_number(
    default_game_with_3_players,
):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    expected_card_count = sess.currently_active_card.pick
    with pytest.raises(InvalidPlayerAction):
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=sess.players[0].username,
                cards=sess.players[0].cards_in_hand[0 : expected_card_count + 1],
            )
        )


def test_logical_error_when_non_existing_palyer_submits(default_game_with_3_players):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    expected_card_count = sess.currently_active_card.pick
    with pytest.raises(LogicalError):
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user="DWADWADWAGWABAWB",
                cards=sess.players[0].cards_in_hand[0:expected_card_count],
            )
        )


def test_invalid_player_action_when_submitting_not_owned_cards(
    default_game_with_3_players,
):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    normal_players = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]
    active_card_picks = sess.currently_active_card.pick
    for player in normal_players:
        with pytest.raises(InvalidPlayerAction):
            sess.player_submit_card(
                PlayerSubmitCards(
                    submitting_user=player.username,
                    cards=sess.white_cards[0:active_card_picks],
                )  # <- Cheeky stuff in this line,
                # this should come from the player
            )


def test_logical_error_when_selected_winner_submission_does_not_exist(
    default_game_with_3_players,
):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    normal_players = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]
    active_card_picks = sess.currently_active_card.pick
    for player in normal_players:
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=player.username,
                cards=player.cards_in_hand[0:active_card_picks],
            )
        )

    with pytest.raises(InvalidPlayerAction):
        sess.select_winner(
            Submission(
                black_card=sess.currently_active_card,
                white_cards=sess.white_cards[0 : sess.currently_active_card.pick],
            )
        )


def test_game_has_ended_when_ran_out_of_black_cards(default_game_with_3_players):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS
    sess.black_cards = []  # Manually removing leftover black cards from session

    normal_players = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]
    active_card_picks = sess.currently_active_card.pick
    for player in normal_players:
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=player.username,
                cards=player.cards_in_hand[0:active_card_picks],
            )
        )

    assert sess.state == GameStates.TZAR_CHOOSING_WINNER
    the_winner_player: CardsAgainstHumanityPlayer = normal_players[0]
    winning_submission = the_winner_player.submissions[-1]

    with pytest.raises(GameHasEnded):
        sess.select_winner(winning_submission)


def test_game_has_ended_when_ran_out_of_white_cards(default_game_with_3_players):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS
    sess.white_cards = [
        sess.white_cards[-1]
    ]  # Manually removing leftover white cards from session

    normal_players = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]
    active_card_picks = sess.currently_active_card.pick
    for player in normal_players:
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=player.username,
                cards=player.cards_in_hand[0:active_card_picks],
            )
        )

    assert sess.state == GameStates.TZAR_CHOOSING_WINNER
    the_winner_player: CardsAgainstHumanityPlayer = normal_players[0]
    winning_submission = the_winner_player.submissions[-1]

    with pytest.raises(GameHasEnded):
        sess.select_winner(winning_submission)


def test_game_has_ended_when_player_reached_points_to_win(default_game_with_3_players):
    sess: GameStateMachine = default_game_with_3_players

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    normal_players = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]
    active_card_picks = sess.currently_active_card.pick
    for player in normal_players:
        sess.player_submit_card(
            PlayerSubmitCards(
                submitting_user=player.username,
                cards=player.cards_in_hand[0:active_card_picks],
            )
        )

    assert sess.state == GameStates.TZAR_CHOOSING_WINNER
    normal_players[0].points = POINTS_TO_WIN - 1  # Making the next point trigger win.
    the_winner_player: CardsAgainstHumanityPlayer = normal_players[0]
    winning_submission = the_winner_player.submissions[-1]

    with pytest.raises(GameHasEnded):
        sess.select_winner(winning_submission)
