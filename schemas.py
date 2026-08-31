from typing import List, Optional

from pydantic import BaseModel


class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    active: Optional[bool] = True
    administrator: Optional[bool] = False

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    user: int

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class ItemOrderSchema(BaseModel):
    amount: int
    taste: str
    size: str
    unit_price: float

    class Config:
        from_attributes = True


class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    items: List[ItemOrderSchema]

    class Config:
        from_attributes = True
