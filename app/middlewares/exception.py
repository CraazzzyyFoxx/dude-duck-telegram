from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette import status
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)
from starlette.requests import Request
from starlette.responses import Response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
        except RequestValidationError as e:
            response = ORJSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                      content={"detail": jsonable_encoder(e.errors())},
                                      )
        except ValidationError as e:
            logger.exception("What!?")
            response = ORJSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": e.json()}
            )
        except HTTPException as e:
            response = ORJSONResponse({"detail": e.detail}, status_code=e.status_code)
        except ValueError:
            logger.exception("What!?")
            response = ORJSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": [{"msg": "Unknown", "loc": ["Unknown"], "type": "Unknown"}]},
            )
        except Exception:
            logger.exception("What!?")
            response = ORJSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": [{"msg": "Unknown", "loc": ["Unknown"], "type": "Unknown"}]},
            )

        return response
