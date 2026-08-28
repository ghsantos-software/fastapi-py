from fastapi import APIRouter, Depends, HTTPException # importa o APIRouter para criar rotas, Depends para injeção de dependências e HTTPException para tratamento de erros
from sqlalchemy.orm import Session # importa a classe Session do SQLAlchemy para gerenciar sessões de banco de dados
from dependencies import get_session, verify_token # importa as funções get_session e verify_token do arquivo dependencies.py para gerenciar sessões de banco de dados e verificar tokens de autenticação
from schemas import OrderSchema, ItemOrderSchema, ResponseOrderSchema # importa os schemas OrderSchema, ItemOrderSchema e ResponseOrderSchema do arquivo schemas.py para validação de dados
from models import Order, User, ItemOrder # importa as classes Order, User e ItemOrder do arquivo models.py para manipulação de dados do banco de dados
from typing import List # importa a classe List do módulo typing para tipagem de listas

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])

# Rota de teste
@order_router.get("/")
async def orders():
    return{"mensagem": "You have accessed the orders route."}

# Criar pedido
@order_router.get("/")
async def create_order(order_schema: OrderSchema, session: Session = Depends(get_session)): # cria um pedido no banco de dados
    new_order = Order(user=order_schema.id_user)
    session.add(new_order)
    session.commit()
    return{"message": f"Order successfully created. Order ID:{new_order} "}

# Cancelar pedido
@order_router.post("/order/cancel/{id_order}")
async def cancel_order(id_order: int, session: Session = Depends(get_session), user: User = Depends(verify_token)): # verifica se o usuário é administrador ou se o pedido pertence ao usuário
    order = session.query(Order).filter(Order.id==id_order).first() # faz uma busca no banco de dados pelo ID do pedido
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    order.status = "CANCELED"
    session.commit()
    return {
        "message": f"Order number: {id_order} successfully cancelled.", 
        "Order": Order
    }

# Listagem de todos os pedidos
@order_router.get("/list")
async def list_orders(session = Depends(get_session), user: User = Depends(verify_token)): # verifica se o usuário é administrador para listar todos os pedidos
    if not user.administrator:
        raise HTTPException(status_code=401, detail="Without authorization")
    else: 
        orders = session.query(Order).all()
        return {
            "orders":orders
        }

# Adicionar item ao pedido
@order_router.post("/order/add-item/{id_order}")
async def add_item_order(id_order: int,
                         item_order_schema: ItemOrderSchema, 
                         session: Session = Depends(get_session), 
                         user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id==id_order).first()
    if not order:
        raise HTTPException(status_code=400)
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401)
    item_order = ItemOrder(item_order_schema.amount,
                           item_order_schema.taste,
                           item_order_schema.size,
                           item_order_schema.unit_price,
                           id_order)
    session.add(item_order)
    order.calculate_price()
    session.commit()
    return {
        "message": "Item successfully created",
        "item": item_order,
        "price": order.price
    }

# Remover item do pedido
@order_router.post("/order/remove_item/{id_item_order}")
async def remove_item_order(id_item_order: int,
                            session: Session = Depends(get_session),
                            user: User = Depends(verify_token)):
    item_order = session.query(ItemOrder).filter(ItemOrder.id==id_item_order).first()
    order = session.query(Order).filter(Order.id==item_order.order).first()
    if not item_order:
        raise HTTPException(status_code=400, detail="Item not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    session.delete(item_order)
    order.calculate_price()
    session.commit()
    return {
        "message": "Item successfully removed",
        "order": order
    }

# Finalizar pedido
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
        "order": order
    }

# Visualizar 1 pedido especifico
@order_router.get("/order/{id_order}")
async def view_order(id_order: int, session: Session = Depends(get_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id==id_order).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.administrator and user.id != order.user:
        raise HTTPException(status_code=401, detail="Without authorization")
    return {
        "amount_items_order": len(order.items),
        "order": order
    }
   
# Listagem de todos os pedidos de 1 usuario  
@order_router.get("/list/orders-user", response_model=List[ResponseOrderSchema])
async def list_orders(session = Depends(get_session), user: User = Depends(verify_token)):
        orders = session.query(Order).filter(Order.user==user.id).all()
        return orders