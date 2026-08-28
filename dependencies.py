from fastapi import (  # importa o Depends para injeção de dependências e HTTPException para tratamento de erros
    Depends,
    HTTPException,
)
from jose import (  # importa a função jwt para decodificar o token de acesso do usuário e a classe JWTError para tratar erros de decodificação do token
    JWTError,
    jwt,
)
from sqlalchemy.orm import (  # importa a classe Session do SQLAlchemy para gerenciar sessões de banco de dados
    Session,
    sessionmaker,
)

from main import (  # importa as variáveis SECRET_KEY, ALGORITHM e oauth2_schema do arquivo main.py para decodificar o token de acesso do usuário
    ALGORITHM,
    SECRET_KEY,
    oauth2_schema,
)
from models import (
    User,  # importa a classe User do arquivo models.py para manipulação de dados do banco de dados
    db,  # importa a variável db do arquivo models.py para criar a conexão com o banco de dados
)


# Sessão do banco de dados
def get_session():
    try:
        Session = sessionmaker(bind=db) # cria a conexão com o banco de dados
        session = Session() # cria uma instância da conexão
        yield session # retorna o valor, mas, não encerra a sessão

    finally: # independe se o try der certo, ou não, ele finaliza
        session.close()


# Verificação se o token é válido 
# Extrair o ID do user do token
def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(get_session)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_user = int(dic_info.get("sub"))
    except JWTError:
            raise HTTPException(status_code=401, detail="Access denied, verify the validity of the token.")
    
    user = session.query(User).filter(User.id==id_user).first()
    if not user:
            raise HTTPException(status_code=401, detail="Access denied")
    return user