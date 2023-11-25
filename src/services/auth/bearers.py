from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request

from src.core import config


class TelegramHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        authorization = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not authorization:
            if self.auto_error:
                raise HTTPException(status_code=403, detail="Not authenticated")
            else:
                return None

        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=authorization)


telegram_oauth2_scheme = TelegramHTTPBearer(bearerFormat="Bearer")
oauth2_scheme = HTTPBearer(bearerFormat="Bearer")


async def requires_authorization_telegram(token=Depends(telegram_oauth2_scheme)):
    if token.credentials == config.app.api_token:
        return token.credentials

    raise HTTPException(status_code=403, detail="Not authenticated") from None


async def requires_authorization(token=Depends(oauth2_scheme)):
    if token.credentials == config.app.api_token:
        return token.credentials

    raise HTTPException(status_code=403, detail="Not authenticated") from None
