from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import Response
import uvicorn, time, requests
from threading import Timer
import db_class

app = FastAPI()

class Tanque(BaseModel):
    quantidade: float

Oleo = Tanque(quantidade= 0.00)

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
        print("Óleo enviado:", disponivel)
        # payload = {"Oleo" : disponivel }
        # response = requests.post("http://127.0.0.1:8888/reator", json= payload )
        # while response.status_code != 200:
        #   time.sleep(1)
        #   response = requests.post(f'http://127.0.0.1:8888/tanque_oleo', json=payload)
    print(tabela.get("quantidade"))
    tabela.end_connection()
    t = Timer(1, regra_negocio)
    t.start()

@app.post("/tanque_oleo")
def insere_oleo_residual(Tanque: Tanque):
    global tabela
    tabela.begin_connection()
    oleo_atual = tabela.get("quantidade")
    oleo_novo = oleo_atual + Tanque.quantidade
    tabela.update("quantidade",oleo_novo)
    tabela.end_connection()
    return{"Mensagem":"Óleo adicionado com sucesso."}


tabela = db_class.SimpleDB("tabela", quantidade = 0.00)

if __name__ == "__main__":
    t = Timer(1, regra_negocio)
    t.start()
    uvicorn.run("tanque_oleo:app", host="127.0.0.1", port=int(3333), log_level="info", reload=True)

