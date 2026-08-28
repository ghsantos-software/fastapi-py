from datetime import (  # importa as classes datetime, timedelta e timezone do módulo datetime para manipulação de datas e horários
    datetime,
    timedelta,
    timezone,
)

from fastapi import (  # importa o APIRouter para criar rotas, Depends para injeção de dependências e HTTPException para tratamento de erros
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import (
    OAuth2PasswordBearer,  # importa a classe OAuth2PasswordBearer para criar o esquema de autenticação OAuth2 com senha e token de acesso
)
from jose import (  # importa a função jwt para decodificar o token de acesso do usuário e a classe JWSError para tratar erros de decodificação do token
    jwt,
)
from sqlalchemy.orm import (
    Session,  # importa a classe Session do SQLAlchemy para gerenciar sessões de banco de dados
)

from dependencies import (  # importa as funções get_session e verify_token do arquivo dependencies.py para gerenciar sessões de banco de dados e verificar tokens de autenticação
    get_session,
    verify_token,
)
from main import (  # importa as variáveis bcrypt_content, ALGORITHM, ACESS_TOKEN_EXPIRE_MINUTES e SECRET_KEY do arquivo main.py para criar o contexto de criptografia de senhas e decodificar o token de acesso do usuário
    ACESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    bcrypt_content,
)
from models import (
    User,  # importa a classe User do arquivo models.py para manipulação de dados do banco de dados
)
from schemas import (  # importa os schemas UserSchema e LoginSchema do arquivo schemas.py para validação de dados
    LoginSchema,
    UserSchema,
)

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
