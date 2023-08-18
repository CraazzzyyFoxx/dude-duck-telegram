from pydantic import BaseModel, EmailStr, Field, field_validator, FieldValidationInfo
from beanie import PydanticObjectId


__all__ = ("LoginForm", "SignInForm", "RegisterResponse")


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    message_id: int


class SignInForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    username: str = Field(min_length=3, max_length=25)
    discord: str = Field(min_items=3)
    message_id: int

    @field_validator('discord')
    def discord_validate(cls, v: str, info: FieldValidationInfo) -> str:
        if v.startswith("@"):
            v = v.replace("@", "")

        if "#" in v:
            name, dis = v.strip("#")
            if len(dis) != 4:
                raise ValueError("The discord username should be @craaazzzyyfoxx or CraazzzyyFoxx#0001 format")
        return v


class RegisterResponse(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    is_activa: bool
    is_superuser: bool
