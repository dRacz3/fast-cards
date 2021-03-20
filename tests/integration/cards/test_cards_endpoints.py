def test_get_white_cards(valid_user_token, test_client):
    token = valid_user_token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    card_data = {
        "card_id": 5,
        "text": "card text",
        "icon": "deck icon",
        "deck": "deck name",
    }
    r = test_client.put(
        "/cards/white",
        json=card_data,
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json() == card_data


def test_get_black_cards(valid_user_token, test_client):
    token = valid_user_token
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    card_data = {
        "card_id": 5,
        "text": "card text",
        "icon": "deck icon",
        "deck": "deck name",
        "pick" : 1
    }
    r = test_client.put(
        "/cards/black",
        json=card_data,
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json() == card_data
