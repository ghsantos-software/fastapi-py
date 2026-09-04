# tarefas-api

[![CI](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml/badge.svg)](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml)

🔗 **Demo:** https://fastapi-py-ptd6.onrender.com/docs
> Free tier — a primeira requisição após inatividade leva ~50s (o serviço "dorme").

API REST pequena para gerenciar tarefas, feita como projeto de estudo de
**DevOps**: o foco não é a API em si, e sim a esteira em volta dela — container,
migrações, CI/CD e deploy automático.

## O que a API faz

| Método | Rota | O quê |
|---|---|---|
| `GET` | `/saude` | health check |
| `GET` | `/tarefas` | lista as tarefas |
| `POST` | `/tarefas` | cria uma tarefa (`{"titulo": "..."}`) |
| `PATCH` | `/tarefas/{id}/concluida` | marca como concluída |

Documentação interativa em `/docs`.

## Stack

- **API:** FastAPI + Uvicorn (Python 3.12)
- **Banco:** PostgreSQL via SQLAlchemy (SQLite como fallback sem Docker)
- **Migrações:** Alembic
- **Qualidade:** Ruff (lint) + Pytest
- **Container:** Docker + Docker Compose
- **CI:** GitHub Actions (lint, migrações, testes, build da imagem)
- **IaC:** Terraform (exemplo de repositório ECR, validado no CI)
- **Deploy:** Render + Neon (PostgreSQL) — free tier

## Rodando com Docker (recomendado)

```bash
cp .env.example .env
docker compose up --build
