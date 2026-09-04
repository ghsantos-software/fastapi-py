# imagem base: Python 3.12 "slim" (Debian enxuto, sem compiladores)
FROM python:3.12-slim

# logs saem na hora (não ficam presos num buffer); não gera .pyc na imagem
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# usuário sem privilégios (não rodar como root)
RUN useradd --create-home appuser

# 1) dependências primeiro (camada cacheável).
#    --only-binary=:all: recusa pacotes que só têm código-fonte,
#    evitando execução de setup.py durante a instalação.
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# 2) só os arquivos que a aplicação precisa (nada de "COPY . .").
#    Copiados como root (dono root, sem escrita para o appuser): se a app
#    for comprometida, o atacante não consegue reescrever o próprio código.
COPY main.py database.py alembic.ini docker-entrypoint.sh ./
COPY alembic ./alembic

USER appuser

# porta que a app escuta (só documentação; não publica nada sozinho)
EXPOSE 8000

# ao iniciar o container: roda a migração e sobe o servidor
CMD ["sh", "docker-entrypoint.sh"]
