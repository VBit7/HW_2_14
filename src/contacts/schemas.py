import pydantic

from datetime import date, datetime
from typing import Optional

import src.auth.schemas as auth_schemas


class ContactSchema(pydantic.BaseModel):
    first_name: str = pydantic.Field(default="John", min_length=3, max_length=50)
    last_name: str = pydantic.Field(default="Brown", min_length=3, max_length=50)
    email: pydantic.EmailStr = "example@example.com"
    phone_number: str = pydantic.Field(default="+38(050)111-22-33", min_length=3, max_length=50)
    date_of_birth: date = pydantic.Field(default=date.today())
    additional_data: Optional[str] = pydantic.Field(None, min_length=1, max_length=250)


class ContactResponse(pydantic.BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: str
    phone_number: str
    date_of_birth: date
    additional_data: str
    created_at: datetime | None
    updated_at: datetime | None
    user: auth_schemas.UserResponse | None


    class Config:
        from_attributes = True
