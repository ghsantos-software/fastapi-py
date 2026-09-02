from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    active: Optional[bool] = True
    administrator: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    user: int

    model_config = ConfigDict(from_attributes=True)


class LoginSchema(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(from_attributes=True)


class ItemOrderSchema(BaseModel):
    amount: int
    taste: str
    size: str
    unit_price: float

    model_config = ConfigDict(from_attributes=True)


class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    items: List[ItemOrderSchema]

    model_config = ConfigDict(from_attributes=True)
