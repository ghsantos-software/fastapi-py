from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from dependencies import get_session, verify_token
from main import ACESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from models import User
from schemas import LoginSchema, UserSchema
from security import hash_password, verify_password

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(id_user, token_duration=timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)):
    expiration_date = datetime.now(timezone.utc) + token_duration
    dic_info = {"sub": str(id_user), "exp": expiration_date}
    jwt_encoded = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)
    return jwt_encoded

def authenticate_user(email, password, session):
    user = session.query(User).filter(User.email==email).first()
    if not user:
        return False
    elif not verify_password(password, user.password):
        return False
    return user

@auth_router.get("/")
async def home():
    return{"mensagem": "You have accessed the default authentication route.", "authenticate": False}

@auth_router.post("/create_account")
async def create_account(user_schema: UserSchema, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email==user_schema.email).first()
    if user:
        raise HTTPException(status_code=400, detail="User email already registered!")

    else:
        encrypted_password = hash_password(user_schema.password)
        new_user = User(user_schema.name, user_schema.email, encrypted_password, user_schema.active, user_schema.administrator)
        session.add(new_user)
        session.commit()
        return{"message": f"User successfully registered {user_schema.email}"}

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

@auth_router.get("/refresh")
async def use_refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
        "access token": access_token,
        "token_type": "Bearer"
        }
