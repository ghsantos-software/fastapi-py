import os

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACESS_TOKEN_EXPIRE_MINUTES", "30")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

# Importa main primeiro: carrega todas as rotas e resolve o import circular.
from main import app  # noqa: E402

# Banco de teste: SQLite na memória, uma conexão só compartilhada (StaticPool).
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=test_engine, autoflush=False)


@pytest.fixture
def session():
    # cria as tabelas antes do teste e apaga depois (cada teste começa limpo)
    from models import Base

    Base.metadata.create_all(bind=test_engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(session):
    # troca o get_session real pelo banco de teste durante o teste
    from dependencies import get_session

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()