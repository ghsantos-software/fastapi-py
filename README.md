# tarefas-api

[![CI](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml/badge.svg)](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml)
[![Terraform](https://github.com/ghsantos-software/fastapi-py/actions/workflows/terraform.yml/badge.svg)](https://github.com/ghsantos-software/fastapi-py/actions/workflows/terraform.yml)

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

- **API:** FastAPI + Uvicorn (Python 3.14)
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
```

Sobe em http://localhost:8000 (`/docs`). As migrações rodam automaticamente na
subida do container; os dados do PostgreSQL ficam num volume nomeado.

## Rodando sem Docker

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn main:app --reload
```

Sem `DATABASE_URL` definida, a aplicação usa um arquivo SQLite local (`tarefas.db`).

## Testes e lint

```bash
pytest
ruff check .
```

## Migrações

```bash
alembic upgrade head                              # aplica as pendentes
alembic revision --autogenerate -m "descrição"    # gera uma nova a partir dos modelos
```

## Configuração (`.env`)

| Variável | Obrigatória | Padrão |
|---|---|---|
| `APP_NAME` | não | `api-tarefas` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | sim (Docker) | — |
| `DATABASE_URL` | não | arquivo SQLite |

## Estrutura

```
main.py               Aplicação FastAPI (rotas)
database.py            Conexão com o banco + modelo Tarefa
Dockerfile              Imagem da aplicação
.dockerignore           O que não entra na imagem
docker-entrypoint.sh    Aplica migrações e sobe o servidor
docker-compose.yml      Stack local (API + PostgreSQL)
alembic/                Migrações
tests/                  Testes (SQLite isolado)
infra/                  Terraform (exemplo, validado no CI)
.github/workflows/      CI (ci.yml) e Terraform (terraform.yml)
.github/dependabot.yml  Atualização automática de dependências
docs/postmortems/       Incidentes anteriores e o que aprendi
```

## CI/CD

A cada push e pull request, o GitHub Actions roda:

- **quality** — Ruff, `alembic upgrade head` + `alembic check` (divergência entre
  modelos e migrações), e Pytest, tudo contra um PostgreSQL descartável.
- **docker** — builda a imagem e roda um smoke test (`import main` dentro dela).
- **validate** — `terraform fmt` + `terraform validate` na pasta `infra/`, só
  quando ela muda.

Merge na `main` dispara re-deploy automático no Render. O Dependabot mantém as
dependências (Python, Docker, GitHub Actions) atualizadas semanalmente.

