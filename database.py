import os

from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# pega a URL do banco de dados a partir da variável de ambiente DATABASE_URL, ou usa SQLite local como padrão.
URL_BANCO = os.getenv("DATABASE_URL", "sqlite:///./tarefas.db")


argumentos = {"check_same_thread": False} if URL_BANCO.startswith("sqlite") else {}
engine = create_engine(URL_BANCO, connect_args=argumentos) 

# "Fábrica" de sessões. Cada requisição HTTP pega uma sessão nova daqui.
Sessao = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Classe base: todo modelo (tabela) herda dela.
Base = declarative_base()


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    concluida = Column(Boolean, nullable=False, default=False)


def obter_banco():
    """Abre uma sessão, entrega para a rota e garante o fechamento."""
    banco = Sessao()
    try:
        yield banco
    finally:
        banco.close()

