FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# usuário não-root criado ANTES de copiar o código
RUN useradd --create-home --uid 1000 appuser

COPY requirements.txt .

# --only-binary força só wheels: nunca executa setup.py de um sdist (igual ao CI)
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# copiado como root: appuser lê e executa, mas não pode modificar o código
COPY main.py models.py schemas.py dependencies.py auth_routes.py order_routes.py \
    alembic.ini docker-entrypoint.sh ./
COPY alembic/ ./alembic/

USER appuser

EXPOSE 8000

# entrypoint roda as migrações e depois faz exec do CMD
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]