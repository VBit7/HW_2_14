from pydantic import BaseModel, EmailStr, Field, ConfigDict
import src.auth.models as auth_models


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=15)


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: str | None
    role: auth_models.Role

    model_config = ConfigDict(from_attributes=True)  # noqa
    # class Config:
    #     from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
