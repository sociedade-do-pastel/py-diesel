from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import Response
import uvicorn, time, requests
from threading import Timer
import db_class, sys

port = int(sys.argv[1])

tabela = db_class.SimpleDB("tanque_oleo", quantidade = 0.00)

app = FastAPI()

class Tanque(BaseModel):
    quantidade: float

def regra_negocio():
    global tabela
    disponivel = 0
    tabela.begin_connection()
    quantidade = tabela.get("quantidade")
    if quantidade <=0.0:
        tem_oleo = 0
    elif quantidade >=0.5:
        tem_oleo = 1
        disponivel = 0.5
        quantidade = quantidade - 0.5
    elif quantidade <0.5:
        tem_oleo = 1
        disponivel = quantidade
        quantidade = quantidade - quantidade
    if tem_oleo == 1:
        tabela.update("quantidade", quantidade)
        payload = {"qtde_oleo" : disponivel }
        response = requests.post(f"http://127.0.0.1:{port+1}/reator/oleo", json= payload)
        while response.status_code != 200:
          time.sleep(1)
          response = requests.post(f'http://127.0.0.1:{port+1}/reator/oleo', json=payload)
    tabela.end_connection()
    time.sleep(1)
    t = Timer(0, regra_negocio)
    t.start()

@app.post("/tanque_oleo")
def insere_oleo_residual(Tanque: Tanque):
    global tabela
    tabela.begin_connection()
    tabela.increment("quantidade", Tanque.quantidade)
    oleo_novo = tabela.get("quantidade")
    tabela.end_connection()
    return {"oleo_atual": oleo_novo}

if __name__ == "__main__":
    t = Timer(0, regra_negocio)
    t.start()
    uvicorn.run("tanque_oleo:app", host="127.0.0.1", port=port, log_level="info", reload=True)