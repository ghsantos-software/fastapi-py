# Rotas quebradas com o CI passando + uma dependência antiga com falha de segurança

| | |
|---|---|
| **Data** | 2026-09-02 |
| **Serviço** | fastapi-py (API rodando no Render + Neon) |
| **Gravidade** | Baixa |
| **Impacto** | Nenhum — ninguém usava as rotas quebradas |
| **Status** | Resolvido no PR #29 |

## O que aconteceu

Resolvi clonar o projeto do zero, rodar os testes e abrir o `/docs` pra conferir
tudo. Aí percebi que várias rotas de pedido davam erro 500, e a rota de login
por formulário (`/auth/login-form`, que é a que o botão "Authorize" do `/docs`
usa) estava simplesmente quebrada.

O que me pegou de surpresa foi que o CI estava **verde**. Passava tudo. Só que os
testes só cobriam 4 rotas — as outras nunca tinham sido testadas, então ninguém
(nem eu, nem o robô) tinha visto o erro.

Junto disso, quando abri o PR com as correções, o scanner de segurança acusou 3
falhas conhecidas (CVE) numa biblioteca que eu tinha fixado numa versão de
alguns meses atrás e nunca mais atualizei.

## Teve impacto?

Não. As rotas quebradas (`add-item`, `remove_item`, `finish`, `view`, `cancel`,
`list` e `login-form`) não eram chamadas por ninguém. O que eu de fato uso —
criar conta, logar, criar pedido e listar os pedidos do usuário — sempre
funcionou normal.

## Por que aconteceu

1. **Eu nunca tinha escrito teste pra essas rotas.** Algumas devolviam o objeto
   do banco "cru" no lugar de devolver só os campos, e o FastAPI não sabe
   transformar isso em JSON — daí o 500. Sem teste batendo na rota, o CI passava
   igual.
2. **A rota de login por formulário usava a classe errada** pra ler usuário e
   senha (`OAuth2PasswordBearer` em vez de `OAuth2PasswordRequestForm`).
3. **Fixei uma dependência e esqueci dela.** O Dependabot só me avisa quando sai
   versão nova; ele não fica revendo se a versão que eu escolhi ganhou algum
   problema de segurança depois.
4. **A coluna `amount` estava como texto** desde o começo do projeto, e o cálculo
   do preço tentava multiplicar número por texto.

## Como eu descobri

Na mão: clonei limpo, rodei `pytest`, li o `/docs` rota por rota. As falhas de
segurança quem apontou foi o scanner do CI, não eu.

## O que me salvou

- O scanner de dependência travou o PR antes do merge — os 3 CVEs não passaram.
- O CI já sobe um Postgres de verdade e roda as migrações, então dava pra testar
  a mudança de coluna com segurança.

## O que eu aprendi

- **CI verde não quer dizer que a API funciona.** Quer dizer que o que eu testei
  funciona. Se a rota não tem teste, ela pode estar quebrada e eu não fico
  sabendo.
- Toda rota nova merece pelo menos um teste simples ("ela responde 200?").
- Dependência fixada também envelhece. Fixar a versão não é "resolvi e esqueci".

## O que ainda falta fazer

- [ ] Fazer o CI falhar se a cobertura de testes cair de uns 85%
- [ ] Colocar no checklist do PR: "rota nova tem teste?"