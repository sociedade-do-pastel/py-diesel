from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import Response
import uvicorn
import time
import requests
from threading import Timer
import db_class
import sys

port = int(sys.argv[1])
tabela = db_class.SimpleDB("tanque_oleo", quantidade=0.00)
orquestrador = db_class.get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("to_qtde_oleo", 0.0)
orquestrador.end_connection()

app = FastAPI()


class Tanque(BaseModel):
    quantidade: float


def regra_negocio():
    global tabela
    global orquestrador
    disponivel = 0
    tabela.begin_connection()
    orquestrador.begin_connection()
    quantidade = tabela.get("quantidade")
    if quantidade <= 0.0:
        tem_oleo = 0
    elif quantidade >= 0.5:
        tem_oleo = 1
        disponivel = 0.5
        quantidade = quantidade - 0.5
    elif quantidade < 0.5:
        tem_oleo = 1
        disponivel = quantidade
        quantidade = quantidade - quantidade
    if tem_oleo == 1:
        tabela.update("quantidade", quantidade)
        orquestrador.update("to_qtde_oleo", quantidade)
        payload = {"qtde_oleo": disponivel}
        response = requests.post(
            f"http://127.0.0.1:{port+1}/reator/oleo", json=payload)
        while response.status_code != 200:
            time.sleep(1)
            response = requests.post(
                f'http://127.0.0.1:{port+1}/reator/oleo', json=payload)
    orquestrador.end_connection()
    tabela.end_connection()
    time.sleep(1)
    t = Timer(0, regra_negocio)
    t.start()


@app.post("/tanque_oleo")
def insere_oleo_residual(Tanque: Tanque):
    global tabela
    global orquestrador
    orquestrador.begin_connection()
    tabela.begin_connection()
    tabela.increment("quantidade", Tanque.quantidade)
    orquestrador.increment("to_qtde_oleo", Tanque.quantidade)
    oleo_novo = tabela.get("quantidade")
    tabela.end_connection()
    orquestrador.end_connection()
    return {"oleo_atual": oleo_novo}


if __name__ == "__main__":
    t = Timer(0, regra_negocio)
    t.start()
    uvicorn.run("tanque_oleo:app", host="127.0.0.1",
                port=port, log_level="info", reload=True)
