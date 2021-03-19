# reference:
# https://testdriven.io/blog/fastapi-jwt-auth/
import time
from typing import Optional

import jwt


from pydantic import BaseModel

# TODO: replace with env vars.
JWT_SECRET = "seceret"
JWT_ALGORITHM = "HS256"


class TokenResponse(BaseModel):
    access_token: str


class TokenContent(BaseModel):
    user_id: str
    expires: float


def signJWT(user_id: str) -> TokenResponse:
    payload = TokenContent(user_id=user_id, expires=time.time() + 600)
    token = jwt.encode(payload.dict(), JWT_SECRET, algorithm=JWT_ALGORITHM)
    return TokenResponse(access_token=token)


def decodeJWT(token: str) -> Optional[TokenContent]:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        token = TokenContent(**decoded_token)
        return token if token.expires >= time.time() else None
    except:
        return None
