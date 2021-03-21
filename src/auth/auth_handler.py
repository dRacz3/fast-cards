# reference:
# https://testdriven.io/blog/fastapi-jwt-auth/
import time
from typing import Optional

import jwt

from src.auth.models import TokenResponse, TokenContent
from src.config import get_settings


def signJWT(user_id: str) -> TokenResponse:
    payload = TokenContent(user_id=user_id, expires=time.time() + 3600)
    token = jwt.encode(
        payload.dict(),
        get_settings().JWT_SECRET,
        algorithm=get_settings().JWT_ALGORITHM,
    )
    return TokenResponse(access_token=token)


def decodeJWT(token: str) -> Optional[TokenContent]:
    try:
        decoded_token = jwt.decode(
            token, get_settings().JWT_SECRET, algorithms=[get_settings().JWT_ALGORITHM]
        )
        token_response = TokenContent(**decoded_token)
        return token_response if token_response.expires >= time.time() else None
    except Exception:
        return None
