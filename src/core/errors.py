from fastapi import HTTPException
from pydantic import BaseModel


class ApiException(BaseModel):
    msg: str
    code: str


class ApiHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: list[ApiException],
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=[e.model_dump(mode="json") for e in detail],
            headers=headers,
        )


class AuthorizationExpired(Exception):
    pass


class InternalServerError(Exception):
    pass


class ServerNotResponseError(Exception):
    pass
