# fastapi-py

[![CI](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml/badge.svg)](https://github.com/ghsantos-software/fastapi-py/actions/workflows/ci.yml)

Uma pequena API REST para gerenciamento de usuários e pedidos, desenvolvida como projeto de estudo para praticar um fluxo completo de engenharia de software, incluindo **containers, migrações, CI, atualização automatizada de dependências, proteção de branches e análise de código**.

## Funcionalidades

* Autenticação JWT (cadastro, login e atualização de token)
* Gerenciamento de pedidos e itens de pedidos, vinculados ao usuário autenticado
* Estrutura do banco de dados gerenciada por migrações com Alembic
* Documentação interativa da API disponível em `/docs`

## Tecnologias utilizadas

* **API:** FastAPI + Uvicorn (Python 3.14)
* **Banco de dados:** PostgreSQL com SQLAlchemy (SQLite como alternativa para execução local sem Docker)
* **Migrações:** Alembic
* **Autenticação:** JWT (`python-jose`) + hash de senhas com `bcrypt`
* **Ferramentas:** Ruff (análise e padronização de código), Pytest + Coverage
* **DevOps:** Docker, Docker Compose, GitHub Actions e Dependabot

## Executando com Docker (recomendado)

```bash
cp .env.example .env
```

Depois, configure uma `SECRET_KEY` real no arquivo `.env`.

Execute:

```bash
docker compose up --build
```

A API estará disponível em:

```text
http://localhost:8000
```

A documentação interativa pode ser acessada em:

```text
http://localhost:8000/docs
```
