# O primeiro deploy não subiu porque faltou um arquivo dentro da imagem Docker

| | |
|---|---|
| **Data** | 2026-09-01 |
| **Serviço** | fastapi-py (Render + Neon) |
| **Gravidade** | Alta — o serviço não subiu |
| **Impacto** | Nenhum — era o primeiro deploy, ninguém usava ainda |
| **Tempo até resolver** | Uns 15 minutos |
| **Status** | Resolvido |

## O que aconteceu

Foi a primeira vez que subi a API no Render. O build da imagem passou, as
migrações do banco rodaram certinho, mas na hora de ligar o servidor deu:

```
ModuleNotFoundError: No module named 'security'
```

Ou seja: a aplicação tentou importar o `security.py` (que faz o hash da senha) e
esse arquivo simplesmente não estava dentro da imagem.

## Teve impacto?

Não. Era o primeiro deploy, sem ninguém usando. O banco também ficou de boa,
porque as migrações rodam **antes** do servidor ligar — então não teve banco
pela metade.

## Como foi rolando

| Hora (mais ou menos) | O que rolou |
|---|---|
| 18:22 | Criei o serviço no Render, primeiro build a partir do `Dockerfile`. |
| 18:23 | Deploy falha ao ligar: `ModuleNotFoundError: No module named 'security'`. As migrações já tinham rodado. |
| 18:30 | Achei o motivo: o `Dockerfile` copia arquivo por arquivo, e `security.py` não estava nessa lista. |
| 18:34 | Merge do PR de correção (`fix(docker): copy security.py into the image`). |
| 18:35 | Render re-deploya sozinho. Serviço no ar. Testei cadastro → login → pedido em produção, tudo ok. |

## Por que aconteceu

Meu `Dockerfile` não usa `COPY . .` (que copiaria a pasta inteira). Ele lista os
arquivos um por um (`COPY main.py models.py ... ./`), pra não jogar segredo e
lixo dentro da imagem e pra não levantar alerta no scanner de segurança.

O problema: quando criei o `security.py` num PR anterior, **esqueci de adicionar
ele nessa lista**. Daí em diante a imagem passou a ser construída sem o arquivo,
e eu não percebi.

E teve um detalhe que escondeu o erro: o passo do CI que builda a imagem
**só buildava, nunca rodava** a imagem. Então "a imagem foi construída" ficava
verde mesmo faltando um arquivo. O outro teste de import do CI rodava em cima do
código clonado (onde o `security.py` existe), não em cima da imagem.

## Como eu descobri

Na marra: o deploy falhou e o erro apareceu no log do Render, já apontando o
nome do arquivo.

## O que me salvou

- As migrações rodam antes do servidor, então o banco não ficou quebrado.
- O deploy automático do Render: bastou o merge pra correção ir pro ar.
- A mensagem de erro era direta e dizia exatamente qual módulo faltava.

## O que eu aprendi

- **"A imagem buildou" não é o mesmo que "a imagem roda".** Tem que ligar a
  imagem no CI, nem que seja só pra fazer um `import`.
- Copiar arquivo por arquivo no `Dockerfile` é frágil: todo arquivo novo é uma
  chance de esquecer.

## O que já fiz e o que falta

| Item | Situação |
|---|---|
| Adicionar `security.py` no `COPY` do `Dockerfile` | ✅ feito |
| CI agora carrega a imagem e roda `python -c "import main"` **dentro dela** | ✅ feito |
| Decidir entre lista explícita e `COPY . .` com um `.dockerignore` bom | ⏳ pendente — `COPY . .` faz voltar um alerta do SonarCloud, então por ora fiquei com a lista + o teste de import como rede de segurança |
