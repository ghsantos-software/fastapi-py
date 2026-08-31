# fastapi-py

[![CI](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml/badge.svg)](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml)

Uma pequena API REST para gerenciamento de usuários e pedidos, desenvolvida como
projeto de estudo para praticar um fluxo completo de engenharia de software:
containers, migrações, CI, atualização automatizada de dependências, proteção de
branches e análise de código.

## Funcionalidades

- Autenticação JWT (cadastro, login e refresh)
- Pedidos e itens de pedido, vinculados ao usuário autenticado
- Estrutura do banco gerenciada por migrações Alembic
- Documentação interativa da API em `/docs`

## Tecnologias

- **API:** FastAPI + Uvicorn (Python 3.14)
- **Banco de dados:** PostgreSQL via SQLAlchemy (SQLite como alternativa para rodar local sem Docker)
- **Migrações:** Alembic
- **Autenticação:** JWT (`python-jose`) + hash de senha com `bcrypt`
- **Qualidade:** Ruff (lint), Pytest + cobertura
- **DevOps:** Docker, Docker Compose, GitHub Actions, Dependabot

## Executando com Docker (recomendado)

```bash
cp .env.example .env
```

Configure uma `SECRET_KEY` real no `.env`, depois:

```bash
docker compose up --build
```

A API sobe em http://localhost:8000 (docs em `/docs`). As migrações rodam
automaticamente na subida; os dados do PostgreSQL ficam num volume nomeado.

## Desenvolvimento local (sem Docker)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn main:app --reload
```

Aponte `DATABASE_URL` para um PostgreSQL local, ou deixe sem definir para usar um
arquivo SQLite.

## Testes e lint

```bash
pytest
ruff check .
```

Os testes rodam contra um banco isolado em memória e mostram a cobertura.

## Migrações do banco

```bash
alembic upgrade head
alembic revision -m "descreva a mudança"
```

## Configuração (`.env`)

| Variável | Obrigatória | Padrão |
|---|---|---|
| `SECRET_KEY` | sim | — |
| `ALGORITHM` | não | `HS256` |
| `ACESS_TOKEN_EXPIRE_MINUTES` | não | `30` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | sim (Docker) | — |
| `DATABASE_URL` | não | arquivo SQLite |

## Estrutura do projeto

```
main.py              Ponto de entrada, config, registro das rotas
models.py            Modelos SQLAlchemy
schemas.py           Schemas Pydantic
security.py          Funções de hash de senha
dependencies.py      Sessão do banco + verificação de token
auth_routes.py       Endpoints /auth
order_routes.py      Endpoints /orders
alembic/             Migrações
tests/               Suíte de testes (banco isolado)
Dockerfile           Imagem da aplicação
docker-compose.yml   Stack local (API + PostgreSQL)
.github/             Workflow de CI e config do Dependabot
```

## CI/CD

A cada push e pull request, o GitHub Actions roda:

- **quality** — Ruff, `alembic upgrade head`, `alembic check` (divergência entre
  modelos e migrações), um teste de importação, e o Pytest com cobertura
- **docker-build** — builda a imagem Docker para validar o Dockerfile

A branch `main` é protegida: mudanças só entram via pull request com os checks
verdes. O Dependabot abre PRs semanais de atualização para pip, GitHub Actions e
a imagem base do Docker. SonarCloud e GitGuardian analisam cada PR.

## Roadmap

- [x] Containerização (Dockerfile + Compose)
- [x] PostgreSQL com migrações Alembic
- [x] Pipeline de CI (lint, migrações, testes + cobertura, build da imagem)
- [x] Dependabot, proteção de branch, análise de código
- [ ] Publicar a imagem num registry (GHCR / ECR)
- [ ] Deploy com URL pública
- [ ] Infraestrutura como código (Terraform)
- [ ] Manifests de Kubernetes
