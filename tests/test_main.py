def test_saude(cliente):
    resposta = cliente.get("/saude")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_criar_e_listar_tarefa(cliente):
    resposta = cliente.post("/tarefas", json={"titulo": "comprar leite"})
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["titulo"] == "comprar leite"
    assert corpo["concluida"] is False
    assert corpo["id"] == 1

    resposta = cliente.get("/tarefas")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1 # confirma que a lista tem 1 tarefa


def test_marcar_como_concluida(cliente):
    cliente.post("/tarefas", json={"titulo": "estudar docker"})

    resposta = cliente.patch("/tarefas/1/concluida")
    assert resposta.status_code == 200
    assert resposta.json()["concluida"] is True


def test_marcar_tarefa_inexistente_da_404(cliente):
    resposta = cliente.patch("/tarefas/999/concluida")
    assert resposta.status_code == 404


def test_criar_tarefa_sem_titulo_da_422(cliente):
    resposta = cliente.post("/tarefas", json={})
    assert resposta.status_code == 422