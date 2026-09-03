import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, obter_banco
from main import app

# Banco de teste: SQLite na MEMÓRIA (some quando o processo acaba).
# StaticPool = mantém 1 conexão só, senão o banco em memória "some" entre chamadas.

engine_teste = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessaoTeste = sessionmaker(bind=engine_teste, autoflush=False, autocommit=False)


@pytest.fixture
def cliente():
    # cria as tabelas a partir dos modelos, antes do teste
    Base.metadata.create_all(bind=engine_teste)

    # versão de teste da dependência: usa o banco de teste
    def obter_banco_teste():
        banco = SessaoTeste()
        try:
            yield banco
        finally:
            banco.close()

    # troca o obter_banco real pelo de teste, só durante o teste
    app.dependency_overrides[obter_banco] = obter_banco_teste
    yield TestClient(app)

    # limpeza: cada teste começa do zero
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_teste)