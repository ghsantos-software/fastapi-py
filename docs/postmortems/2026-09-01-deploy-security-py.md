# Postmortem — deploy falho por módulo ausente na imagem

| | |
|---|---|
| **Data** | 2026-09-01 |
| **Serviço** | `fastapi-py` (Render + Neon) |
| **Severidade** | Alta — serviço não subiu |
| **Impacto a usuários** | Nenhum (primeiro deploy do serviço) |
| **Duração** | ~15 min entre o deploy falho e a correção no ar |
| **Status** | Resolvido |

## Resumo

O primeiro deploy da aplicação no Render falhou no boot com
`ModuleNotFoundError: No module named 'security'`. As migrações do banco rodaram
com sucesso, mas o `uvicorn` não conseguiu carregar a aplicação. A causa foi um
módulo da aplicação que não estava na lista de `COPY` do `Dockerfile` — a imagem
era buildada sem ele.

## Impacto

- O serviço `fastapi-py` não ficou disponível até a correção.
- Nenhum usuário afetado: era a primeira publicação, sem tráfego anterior.
- O banco (Neon) ficou consistente — as migrações são aplicadas antes do
  servidor subir.

## Linha do tempo

| Hora (aprox.) | Evento |
|---|---|
| 18:22 | Serviço criado no Render; primeiro build a partir do `Dockerfile`. |
| 18:23 | Deploy falha no boot: `ModuleNotFoundError: No module named 'security'`. Migrações do Alembic já haviam rodado. |
| 18:30 | Causa raiz identificada: o `COPY` explícito do `Dockerfile` não lista `security.py`. |
| 18:34 | PR de correção mergeado (`fix(docker): copy security.py into the image`). |
| 18:35 | Render re-deploya automaticamente. Status `live`. Fluxo cadastro → login → pedido validado em produção. |

## Causa raiz

O `Dockerfile` copia os arquivos da aplicação por **lista explícita**
(`COPY main.py models.py ... ./`) em vez de `COPY . .`. Essa escolha foi feita
para não levar segredos e artefatos para dentro da imagem e para satisfazer a
análise de segurança.

Quando o módulo `security.py` (hashing de senha) foi criado em um PR anterior,
ele **não foi adicionado a essa lista**. A partir daí, a imagem passou a ser
construída sem o arquivo.

## Fatores contribuintes

- O job `docker-build` do CI **buildava** a imagem mas **nunca a executava** —
  então "a imagem builda" ficava verde mesmo com um módulo faltando.
- O passo *Import smoke test* do CI roda contra o código do checkout (onde
  `security.py` existe), não contra a imagem.
- O `security.py` entrou em um PR focado em correção de bugs; o efeito no
  `Dockerfile` passou despercebido na revisão.

## Detecção

Falha no primeiro deploy do serviço no Render (visível nos logs do deploy).

## O que funcionou bem

- As migrações rodam no entrypoint **antes** do servidor: o banco não ficou em
  estado inconsistente.
- O deploy automático do Render transformou a correção em um único merge.
- A mensagem de erro era explícita e apontava o arquivo.

## O que não funcionou

- O CI dava **confiança falsa**: `docker-build` verde não significava "a imagem
  roda".
- `COPY` por lista explícita é frágil a arquivos novos e não tinha rede de
  proteção.

## Ações

| Ação | Status |
|---|---|
| Adicionar `security.py` ao `COPY` do `Dockerfile` | ✅ Feito |
| CI: carregar a imagem (`load`) e rodar `python -c "import main"` **dentro dela** a cada execução | ✅ Feito neste PR |
| Reavaliar `COPY` explícito vs `COPY . .` + `.dockerignore` robusto | ⏳ Pendente — `COPY . .` reintroduz um alerta do SonarCloud; por ora, mantida a lista + o smoke test como rede de proteção |