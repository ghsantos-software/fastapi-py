import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") or "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES") or 30)

# Cria a instância da aplicação FastAPI
app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

# Importa as rotas do arquivo order_routes.py e auth_routes.py
from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)





