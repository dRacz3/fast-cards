from tests.conftest import default_header_with_x_token, default_header


def test_get_all_users(valid_user_token, test_client):
    token = valid_user_token()
    response = test_client.get("/auth/", headers=default_header_with_x_token(token))

    assert response.status_code == 200, f"failure: {response.content.decode()}"
    assert (
        len(response.json()) == 1
    ), "The token holder user should be the only one in the database."


def test_user_login_fails(test_client):
    response = test_client.post(
        "/auth/login",
        json={"email": "abdulazeez@x.com", "password": "weakpassword"},
        headers=default_header(),
    )

    assert response.status_code == 403, f"failure: {response.content.decode()}"
    assert "access_token" not in response.json().keys()


def test_user_signup_then_login_success(test_client):
    signup_response = test_client.post(
        "/auth/signup",
        json={
            "username": "mr. Test user",
            "email": "test@user.com",
            "password": "testpassword12512611",
        },
        headers=default_header(),
    )
    assert signup_response.status_code == 200

    login_response = test_client.post(
        "/auth/login",
        json={"email": "test@user.com", "password": "testpassword12512611"},
        headers=default_header(),
    )

    assert (
        login_response.status_code == 200
    ), f"failure: {login_response.content.decode()}"
    assert "access_token" in login_response.json().keys()
