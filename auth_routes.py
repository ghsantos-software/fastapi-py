from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from dependencies import get_session, verify_token
from main import ACESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, bcrypt_content
from models import User
from schemas import LoginSchema, UserSchema

# Cria o router de autenticação
auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Cria o tokjen de acesso do usuário
def create_token(id_user, token_duration=timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + token_duration
    dic_info = {"sub": str[id_user], "expiration": expiration_date}
    jwt_encoded = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_encoded

# Verifica se o usuário existe no banco de dados e se a senha está correta
def authenticate_user(email, password, session):
    user = session.query(User).filter(User.email==email).first()
    if not user:
        return False
    elif not bcrypt_content.verify(password, user.password):
        return False
    return user

# Verifica se o token de acesso do usuário é válido
@auth_router.get("/")
async def home():
    return{"mensagem": "You have accessed the default authentication route.", "authenticate": False}

# Verifica se o token de acesso do usuário é válido
@auth_router.post("/create_account")
async def create_account(user_schema: UserSchema, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email==user_schema.email).first() # faz uma busca no banco de dados
    if user:
        raise HTTPException(status_code=400, detail="User email already registered!")
    
    else:
        encrypted_password = bcrypt_content.hash(user_schema.password) # processo de criptografia de senha em hash
        new_user = User(user_schema.name, user_schema.email, encrypted_password, user_schema.active, user_schema.administrator)
        session.add(new_user)
        session.commit()
        return{"message": f"User successfully registered {user_schema.email}"}

# Rota de login
@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(get_session)):
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    else:
        access_token = create_token(user.id)
        refresh_token = create_token(user.id, token_duration=timedelta(days=7))
        return {"access token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer"
                }

# Rota de login com formulário
@auth_router.post("/login-form")
async def login_form(from_date: OAuth2PasswordBearer = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(from_date.username, from_date.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    else:
        access_token = create_token(user.id)
        return {"access token": access_token,
                "token_type": "Bearer"
                }

# Rota de refresh token
@auth_router.get("/refresh")
async def use_refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
        "access token": access_token,
        "token_type": "Bearer"
        }
