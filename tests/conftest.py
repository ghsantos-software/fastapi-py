import os

# O conftest.py é carregado pelo pytest ANTES dos testes.
# Defini variáveis de ambiente falsas para o "import main" não quebrar.
# setdefault = só define se ainda não existir (não atropela um .env real).

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACESS_TOKEN_EXPIRE_MINUTES", "30")