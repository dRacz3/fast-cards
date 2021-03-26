from passlib.hash import pbkdf2_sha256  # type: ignore


def hash_password(password: str) -> str:
    hashed_password = pbkdf2_sha256.hash(password)
    return hashed_password


def verify_password(user_provided_password, stored_pw) -> bool:
    return pbkdf2_sha256.verify(user_provided_password, stored_pw)
