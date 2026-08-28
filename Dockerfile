# Imagem base: Python 3.12 enxuto
FROM python:3.12-slim

# Não gera .pyc; logs saem na hora (sem buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Cria usuário sem privilégios e dá posse de /app (o SQLite grava aqui, então o dono precisa poder escrever)
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

# A API escuta na 8000
EXPOSE 8000

# Ao subir: aplica migrações e depois inicia a API. Host 0.0.0.0 = aceitar conexões de fora do container.
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]