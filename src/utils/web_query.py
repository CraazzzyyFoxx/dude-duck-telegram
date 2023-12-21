from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from starlette import status

from src.core import errors
from src.core.bot import bot


async def validate_webapp_init_data(data: dict) -> WebAppInitData:
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except (ValueError, KeyError) as e:
        raise errors.ApiHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[errors.ApiException(msg="Unauthorized", code="unauthorized")],
        ) from e
    return init_data
