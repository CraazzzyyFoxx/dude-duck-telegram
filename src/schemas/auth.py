import re
import typing

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

__all__ = ("LoginForm", "SignInForm", "RegisterResponse")


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    message_id: int


class SignInForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    repeat_password: str = Field(min_length=6)
    username: typing.Annotated[
        str,
        StringConstraints(strip_whitespace=True, to_lower=True, min_length=3, max_length=20),
    ]
    discord: str = Field(min_length=3)
    message_id: int

    @field_validator("discord")
    def discord_validate(cls, v: str) -> str:
        if "#" in v:
            name, dis = v.split("#")
            if len(dis) == 4:
                return v
        if len(v.replace(" ", "")) == len(v):
            return v
        raise ValueError("The discord username should be craaazzzyyfoxx or CraazzzyyFoxx#0001 format")

    @field_validator("username")
    def username_validate(cls, v: str):
        regex = re.fullmatch(r"([a-zA-Z0-9_-]+)", v)
        if not regex:
            raise ValueError("Only Latin, Cyrillic and numbers can be used in the username")
        return v


class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    is_activa: bool
    is_superuser: bool
