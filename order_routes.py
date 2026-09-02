from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_session, verify_token
from models import ItemOrder, Order, User
from schemas import ItemOrderSchema, OrderSchema, ResponseOrderSchema

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])

@order_router.get("/")
async def orders():
    return{"mensagem": "You have accessed the orders route."}

@order_router.post("/order")
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session)):
    new_order = Order(user=order_schema.user)
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return {"message": f"Order successfully created. Order ID: {new_order.id}"}

@order_router.post("/order/cancel/{id_order}")
async def cancel_order(id_order: int, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id==id_order).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    order.status = "CANCELED"
    session.commit()
    return {
        "message": f"Order number: {id_order} successfully cancelled.",
        "status": order.status
    }

@order_router.get("/list", response_model=List[ResponseOrderSchema])
async def list_orders(session = Depends(get_session), user: User = Depends(verify_token)):
    if not user.administrator:
        raise HTTPException(status_code=401, detail="Without authorization")
    else:
        orders = session.query(Order).all()
        return orders

@order_router.post("/order/add-item/{id_order}")
async def add_item_order(id_order: int,
                         item_order_schema: ItemOrderSchema,
                         session: Session = Depends(get_session),
                         user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id==id_order).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    item_order = ItemOrder(item_order_schema.amount,
                           item_order_schema.taste,
                           item_order_schema.size,
                           item_order_schema.unit_price,
                           id_order)
    session.add(item_order)
    session.flush()
    order.calculate_price()
    session.commit()
    return {
        "message": "Item successfully created",
        "item_id": item_order.id,
        "price": order.price
    }

@order_router.post("/order/remove_item/{id_item_order}")
async def remove_item_order(id_item_order: int,
                            session: Session = Depends(get_session),
                            user: User = Depends(verify_token)):
    item_order = session.query(ItemOrder).filter(ItemOrder.id==id_item_order).first()
    if not item_order:
        raise HTTPException(status_code=400, detail="Item not found")
    order = session.query(Order).filter(Order.id==item_order.order).first()
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    session.delete(item_order)
    session.flush()
    order.calculate_price()
    session.commit()
    return {
        "message": "Item successfully removed",
        "order_id": order.id,
        "price": order.price
    }

@order_router.post("/order/finish/{id_order}")
async def finish_order(id_order: int, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id==id_order).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    order.status = "COMPLETED"
    session.commit()
    return {
        "message": f"Order number: {order.id} successfully completed.",
        "status": order.status
    }

@order_router.get("/order/{id_order}")
async def view_order(id_order: int, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id==id_order).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    return {
        "amount_items_order": len(order.items),
        "order": ResponseOrderSchema.model_validate(order)
    }

@order_router.get("/list/orders-user", response_model=List[ResponseOrderSchema])
async def list_one_orders(session = Depends(get_session), user: User = Depends(verify_token)):
    orders = session.query(Order).filter(Order.user==user.id).all()
    return orders