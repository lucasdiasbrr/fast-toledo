from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import arrow

app = FastAPI()

fila = []
clientes_atendidos = []

class Cliente(BaseModel):
    nome: str
    tipo_atendimento: str

class ClienteAtendido(BaseModel):
    nome: str
    tipo_atendimento: str
    posicao: int
    data_chegada: str
    data_atendimento: str

class RespostaAtendimento(BaseModel):
    status: str
    nome: str
    data_atendimento: str

@app.get("/fila", response_model=List[Cliente])
def listar_fila():
    tz_local = 'America/Sao_Paulo'
    fila_local = [
        {
            "nome": cliente["nome"],
            "tipo_atendimento": cliente["tipo_atendimento"],
            "posicao": cliente["posicao"],
            "data_chegada": arrow.get(cliente["data_chegada"]).to(tz_local).format("YYYY-MM-DD HH:mm:ss"),
            "atendido": cliente["atendido"],
        }
        for cliente in fila if not cliente["atendido"]
    ]

    return fila_local

@app.get("/fila/{posicao}", response_model=Cliente)
def obter_cliente(posicao: int):
    if posicao < 0 or posicao >= len(fila) or fila[posicao]["atendido"]:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cliente = fila[posicao]
    cliente_local = {
        "nome": cliente["nome"],
        "tipo_atendimento": cliente["tipo_atendimento"],
        "posicao": cliente["posicao"],
        "data_chegada": arrow.get(cliente["data_chegada"]).to('America/Sao_Paulo').format("YYYY-MM-DD HH:mm:ss"),
        "atendido": cliente["atendido"],
    }
    return cliente_local

@app.post("/fila", response_model=Cliente)
def adicionar_cliente(cliente: Cliente):
    if len(cliente.nome) > 20:
        raise HTTPException(status_code=400, detail="O nome deve ter no máximo 20 caracteres")
    if cliente.tipo_atendimento not in ['N', 'P']:
        raise HTTPException(status_code=400, detail="Tipo de atendimento inválido. Use 'N' ou 'P'")

    tz_local = 'America/Sao_Paulo'
    novo_cliente = {
        "nome": cliente.nome,
        "tipo_atendimento": cliente.tipo_atendimento,
        "posicao": len(fila),
        "data_chegada": arrow.utcnow().to(tz_local).format("YYYY-MM-DD HH:mm:ss"),
        "atendido": False,
    }

    if cliente.tipo_atendimento == "P":
        ultima_posicao_preferencial = max((c["posicao"] for c in fila if c["tipo_atendimento"] == "P"), default=-1)
        novo_cliente["posicao"] = ultima_posicao_preferencial + 1

    for c in fila:
        if c["posicao"] >= novo_cliente["posicao"]:
            c["posicao"] += 1

    fila.insert(novo_cliente["posicao"], novo_cliente)
    return novo_cliente

@app.put("/fila", response_model=RespostaAtendimento)
def atender_cliente():
    if not fila:
        return RespostaAtendimento(status="Sem clientes para atender", nome="", data_atendimento="")

    for i, cliente in enumerate(fila):
        if not cliente["atendido"]:
            cliente["atendido"] = True
            nome_cliente_atendido = cliente["nome"]
            data_atendimento = arrow.utcnow().to('America/Sao_Paulo').format("YYYY-MM-DD HH:mm:ss")

            cliente_atendido = ClienteAtendido(
                nome=nome_cliente_atendido,
                tipo_atendimento=cliente["tipo_atendimento"],
                posicao=cliente["posicao"],
                data_chegada=cliente["data_chegada"],
                data_atendimento=data_atendimento
            )
            clientes_atendidos.append(cliente_atendido)

            fila.pop(i)
            return RespostaAtendimento(status="Cliente atendido", nome=nome_cliente_atendido, data_atendimento=data_atendimento)

    return RespostaAtendimento(status="Todos os clientes foram atendidos", nome="", data_atendimento="")

@app.delete("/fila/{posicao}")
def remover_cliente(posicao: int):
    if posicao < 0 or posicao >= len(fila) or fila[posicao]["atendido"]:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    fila.pop(posicao)

    for i, cliente in enumerate(fila[posicao:], start=posicao):
        cliente["posicao"] -= 1

    return {"message": f"Cliente na posição {posicao} removido"}

@app.get("/atendimentos", response_model=List[ClienteAtendido])
def listar_atendimentos():
    tz_local = 'America/Sao_Paulo'
    atendimentos = [
        {
            "nome": cliente.nome,
            "tipo_atendimento": cliente.tipo_atendimento,
            "posicao": cliente.posicao,
            "data_chegada": arrow.get(cliente.data_chegada).to(tz_local).format("YYYY-MM-DD HH:mm:ss"),
            "data_atendimento": arrow.get(cliente.data_atendimento).to(tz_local).format("YYYY-MM-DD HH:mm:ss"),
        }
        for cliente in clientes_atendidos
    ]

    return atendimentos
