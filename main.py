import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import Tarefa, obter_banco

# pega o nome da aplicação a partir da variável de ambiente APP_NAME
NOME_APLICACAO = os.getenv("APP_NAME", "api-tarefas")

# Instância do FastAPI, com o nome da aplicação definido acima.
app = FastAPI(title=NOME_APLICACAO)


# ---- formato dos dados: o que entra e o que sai ----
class TarefaEntrada(BaseModel):
    titulo: str


class TarefaSaida(BaseModel):
    id: int
    titulo: str
    concluida: bool

    model_config = ConfigDict(from_attributes=True) # permite que o Pydantic converta objetos ORM em dicionários automaticamente


# ---- rotas ----
@app.get("/saude") # rota de verificação de saúde da aplicação
def verificar_saude():
    return {"status": "ok"}


@app.get("/tarefas", response_model=list[TarefaSaida])
def listar_tarefas(banco: Session = Depends(obter_banco)): # dependência que injeta a sessão do banco de dados na função
    return banco.query(Tarefa).all()


@app.post("/tarefas", response_model=TarefaSaida, status_code=201)
def criar_tarefa(
    dados: TarefaEntrada,
    banco: Session = Depends(obter_banco)
):
    tarefa = Tarefa(titulo=dados.titulo)

    banco.add(tarefa)
    banco.commit()
    banco.refresh(tarefa)

    return tarefa


@app.patch("/tarefas/{tarefa_id}/concluida", response_model=TarefaSaida)
def marcar_como_concluida(
    tarefa_id: int,
    banco: Session = Depends(obter_banco)
):
    tarefa = banco.get(Tarefa, tarefa_id)

    if tarefa is None:
        raise HTTPException(
            status_code=404,
            detail="Tarefa não encontrada"
        )

    tarefa.concluida = True

    banco.commit()
    banco.refresh(tarefa)

    return tarefa
