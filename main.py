# uvicorn main:app --reload - código para rodar no terminal 

import os  # importa a biblioteca os para acessar as variáveis de ambiente do sistema operacional

from dotenv import (
    load_dotenv,  # importa a função load_dotenv para carregar as variáveis de ambiente do arquivo .env
)
from fastapi import FastAPI  # importa a classe FastAPI para criar a aplicação web
from fastapi.security import (
    OAuth2PasswordBearer,  # importa a classe OAuth2PasswordBearer para criar o esquema de autenticação OAuth2 com senha e token de acesso
)
from passlib.context import (
    CryptContext,  # importa a classe CryptContext para criar o contexto de criptografia de senhas
)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

# Cria a instância da aplicação FastAPI
app = FastAPI()

bcrypt_content = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login-form")

# Importa as rotas do arquivo order_routes.py e auth_routes.py
from auth_routes import auth_router
from order_routes import order_router

app.include_router(auth_router)
app.include_router(order_router)





