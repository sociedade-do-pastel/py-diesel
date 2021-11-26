import uvicorn
import time
import requests
import db_class
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import Response
from threading import Thread
from datetime import datetime

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

    while True:
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
            response = requests.Response()
            try:
                response = requests.post(
                    f"http://127.0.0.1:{port+1}/reator/oleo", json=payload)
            except Exception:
                pass

            while response.status_code != 200:
                try:
                    time.sleep(1)
                    response = requests.post(
                        f'http://127.0.0.1:{port+1}/reator/oleo', json=payload)
                except Exception:
                    pass

        orquestrador.end_connection()
        tabela.end_connection()
        time.sleep(1)


@app.post("/tanque_oleo")
def insere_oleo_residual(tanque: Tanque):
    global tabela
    global orquestrador
    orquestrador.begin_connection()
    tabela.begin_connection()
    tabela.increment("quantidade", tanque.quantidade)
    oleo_novo = tabela.get("quantidade")
    orquestrador.update("to_qtde_oleo", oleo_novo)
    data = datetime.now()
    print(
        f'{__name__} [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(tanque.quantidade, 3)} DE ÓLEO')
    orquestrador.print_table()
    print()
    tabela.end_connection()
    orquestrador.end_connection()
    return {"oleo_atual": oleo_novo}


if __name__ == "__main__":
    t = Thread(target=regra_negocio, daemon=True)
    t.start()
    uvicorn.run("tanque_oleo:app", host="127.0.0.1",
                port=port, log_level="warning", reload=True)
