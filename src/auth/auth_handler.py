# reference:
# https://testdriven.io/blog/fastapi-jwt-auth/

import time
from typing import Dict

import jwt

# TODO: replace with env vars.
from pydantic import BaseModel

JWT_SECRET = "seceret"
JWT_ALGORITHM = "HS256"


class TokenResponse(BaseModel):
    access_token: str


def signJWT(user_id: str) -> TokenResponse:
    payload = {"user_id": user_id, "expires": time.time() + 600}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return TokenResponse(access_token=token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
