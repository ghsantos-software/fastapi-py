#!/bin/sh
# ============================================================
# docker-entrypoint.sh
# Roda toda vez que o container sobe (é o ENTRYPOINT do Dockerfile).
# Aplica as migrações do banco e SÓ ENTÃO entrega o controle pro servidor.
# ============================================================

# "set -e" = se qualquer comando abaixo falhar, o script para na hora.
# (não adianta subir a API se a migração quebrou.)
set -e

echo "Applying database migrations..."
# cria/atualiza as tabelas no Postgres até a última migração do Alembic
alembic upgrade head

echo "Starting: $*"
# "$@"  = os argumentos que o container recebeu:
#         o CMD do Dockerfile, ou o "command:" do docker-compose no dev.
# "exec" = substitui ESTE script pelo comando, em vez de rodar como "filho".
#          Assim o uvicorn vira o processo principal (PID 1) e recebe direto
#          o sinal de parada do "docker stop" -> desliga limpo, sem travar.
exec "$@"