import os

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

# URL do banco vem da variável de ambiente; usa SQLite local se não houver
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///banco.db")

db = create_engine(DATABASE_URL)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    email = Column("email", String, nullable=False)
    password = Column("password", String, nullable=False)
    active = Column("status", Boolean)
    administrator = Column("admin", Boolean, default=False)

    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.administrator = admin


class Order(Base):
    __tablename__ = "orders"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    user = Column("user", ForeignKey("users.id"))
    price = Column("price", Float)
    # cascade: apaga os itens junto com o pedido
    items = relationship("ItemOrder", cascade="all, delete")

    def __init__(self, user, status="PENDENT", price=0):
        self.user = user
        self.price = price
        self.status = status

    def calculate_price(self):
        self.price = sum(item.unit_price * item.amount for item in self.items)


class ItemOrder(Base):
    __tablename__ = "Items_Order"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    amount = Column("amount", String)
    taste = Column("taste", String)
    size = Column("size", String)
    unit_price = Column("unit_price", Float)
    order = Column("order", ForeignKey("orders.id"))

    def __init__(self, amount, taste, size, unit_price, order):
        self.amount = amount
        self.taste = taste
        self.size = size
        self.unit_price = unit_price
        self.order = order

