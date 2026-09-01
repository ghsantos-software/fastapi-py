# ============================================================
# Dockerfile — a "receita" da imagem da aplicação.
# Cada instrução vira uma "camada"; o Docker reaproveita as que não mudaram.
# ============================================================

# Imagem base: Python 3.14 na variante "slim" (bem menor que a completa).
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE=1 -> não gera arquivos .pyc (lixo dentro do container)
# PYTHONUNBUFFERED=1        -> print/log aparece na hora, sem ficar preso num buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Pasta de trabalho dentro do container. COPY/RUN daqui pra frente são relativos a /app.
WORKDIR /app

# Cria um usuário comum (sem root) ANTES de copiar o código.
# Rodar como root é risco: se a app for invadida, o atacante já entra limitado.
RUN useradd --create-home --uid 1000 appuser

# Copia SÓ o requirements.txt primeiro (antes do código).
# Enquanto as dependências não mudam, o Docker reaproveita a camada do "pip install"
# e não reinstala tudo a cada alteração no código.
COPY requirements.txt .

# Instala as dependências.
#   --no-cache-dir      -> não guarda cache do pip (imagem menor)
#   --only-binary=:all: -> só pacotes "prontos" (wheels); nunca roda setup.py de um pacote-fonte
RUN pip install --no-cache-dir --only-binary=:all: -r requirements.txt

# Copia o código, arquivo por arquivo de propósito (em vez de "COPY . ."):
#   - não manda sem querer .env, .git, chaves etc. pra dentro da imagem
#   - deixa explícito o que a app precisa pra rodar
# Copiado como root -> o appuser consegue LER e executar, mas não MODIFICAR o código.
COPY main.py models.py schemas.py dependencies.py auth_routes.py order_routes.py \
    security.py alembic.ini docker-entrypoint.sh ./
COPY alembic/ ./alembic/

# Daqui pra frente o container roda como "appuser", não como root.
USER appuser

# Informativo: a aplicação escuta na porta 8000 (não abre nada sozinho).
EXPOSE 8000

# ENTRYPOINT = comando que SEMPRE roda quando o container sobe.
#   -> executa o script que aplica as migrações e depois liga o servidor.
# CMD = argumento padrão passado pro ENTRYPOINT (o comando do servidor).
#   -> dá pra trocar sem mexer no Dockerfile (o compose troca por "uvicorn ... --reload").
ENTRYPOINT ["sh", "docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]