#!/bin/sh
# Roda toda vez que o container inicia.
# 1) aplica as migrações pendentes   2) sobe o servidor

set -e

echo "Aplicando migrações..."
alembic upgrade head

echo "Subindo o servidor na porta ${PORT:-8000}..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"