from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker

from main import ALGORITHM, SECRET_KEY, oauth2_schema
from models import User, db]

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