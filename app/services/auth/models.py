import re

from pydantic import BaseModel, EmailStr, Field, field_validator, constr
from beanie import PydanticObjectId

__all__ = ("LoginForm", "SignInForm", "RegisterResponse")


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    message_id: int


class SignInForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    repeat_password: str = Field(min_length=6)
    username: constr(strip_whitespace=True, to_lower=True, min_length=3, max_length=20)
    discord: str = Field(min_length=3)
    message_id: int

    @field_validator('discord')
    def discord_validate(cls, v: str) -> str:
        if v.startswith("@"):
            if len(v.replace(" ", "")) != len(v):
                raise ValueError("The discord username should be @craaazzzyyfoxx or CraazzzyyFoxx#0001 format")
        elif "#" in v:
            name, dis = v.strip("#")
            if len(dis) != 4:
                raise ValueError("The discord username should be @craaazzzyyfoxx or CraazzzyyFoxx#0001 format")
        else:
            raise ValueError("The discord username should be @craaazzzyyfoxx or CraazzzyyFoxx#0001 format")
        return v

    @field_validator('username')
    def username_validate(cls, v: str):
        regex = re.fullmatch(r"([\w{L}]+)", v)
        if not regex:
            raise ValueError("Only Latin, Cyrillic and numbers can be used in the username")
        return v


class RegisterResponse(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    is_activa: bool
    is_superuser: bool
