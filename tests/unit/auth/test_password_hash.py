from src.auth.password_hash import hash_password, verify_password


def test_password_hashing():
    pw = "hello_jokes_on_you"
    hash = hash_password(pw)
    assert not verify_password("some different", hash)
    assert verify_password("hello_jokes_on_you", hash)
