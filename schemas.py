from pydantic import BaseModel # importa a classe BaseModel do módulo pydantic para validação de dados
from typing import Optional, List # importa a classe Optional do módulo typing para tipagem de valores opcionais

# User schema para validação de dados 
class UserSchema(BaseModel):
    name: str 
    email: str
    password: str 
    active: Optional[bool]
    administrator: Optional[bool]

    class Config:
        from_attributes = True # informa que vai ser uma classe transformada em sql no banco de dados (uma conexão com a classe models)

# Login schema para validação de dados
class OrderSchema(BaseModel):
    user: int

    class Config:
        from_attributes = True 

# ItemOrder schema para validação de dados
class LoginSchema(BaseModel):
    email: str
    password: str 

    class Config:
        from_attributes = True 

# ItemOrder schema para validação de dados
class ItemOrderSchema(BaseModel):
    amount: int
    taste: str
    size: str
    unit_price: float

    class Config:
        from_attributes = True 

# Order schema para validação de dados
class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    items: List[ItemOrderSchema] 

    class Config:
        from_attributes = True
