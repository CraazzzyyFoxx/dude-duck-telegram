import typing

from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError
from starlette import status


status_map = {
    status.HTTP_404_NOT_FOUND: "not found",
    status.HTTP_400_BAD_REQUEST: "already exist"
}


class ValidationErrorDetail(BaseModel):
    location: str
    message: str
    error_type: str
    context: dict[str, typing.Any] | None = None


class APIValidationError(BaseModel):
    errors: list[ValidationErrorDetail]

    @classmethod
    def from_pydantic(cls, exc: ValidationError) -> "APIValidationError":
        return cls(
            errors=[
                ValidationErrorDetail(
                    location=" -> ".join(map(str, err["loc"])),
                    message=err["msg"],
                    error_type=err["type"],
                    context=err.get("ctx"),
                )
                for err in exc.errors()
            ],
        )


class BotErrorMessage(BaseModel):
    error: str = Field(
        ...,
        description="Message describing the error",
        examples=["Couldn't communicate with Telegram Bot (HTTP 503 error) : Service Unavailable"],
    )


class InternalServerErrorMessage(BaseModel):
    error: str = Field(
        ...,
        description="Message describing the internal server error",
        examples=[
            (
                "An internal server error occurred during the process."
            )
        ],
    )


class CommonHTTPError(BaseModel):
    """JSON response model for errors raised by :class:`starlette.HTTPException`."""

    detail: str
    extra: dict[str, typing.Any] | None = None


class DudeDuckAPIError(HTTPException):
    pass


class DudeDuckAPINotFound(DudeDuckAPIError):
    prefix = ""

    def __init__(self, **data):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"{self.prefix} ({' '.join([f'{key}={item}' for key, item in data.items()])}) not found"


class DudeDuckAPIAlreadyExist(DudeDuckAPIError):
    prefix = ""

    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = f"{self.prefix} already exist"


class DudeDuckAPIDontPermissions(DudeDuckAPIError):
    prefix = ""

    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = f"Don't have permissions"


class OrderChannelNotFound(DudeDuckAPINotFound):
    prefix = "Order Channel"


class OrderChannelAlreadyExist(DudeDuckAPIAlreadyExist):
    prefix = "Order Channel"


class OrderMessageNotFound(DudeDuckAPINotFound):
    prefix = "Order Message"


class OrderMessageAlreadyExist(DudeDuckAPIAlreadyExist):
    prefix = "Order Message"


class NoLogin(Exception):
    pass


class AuthorizationExpired(Exception):
    pass


class InternalServerError(Exception):
    pass


class ServerNotResponseError(Exception):
    pass

