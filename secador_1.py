from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import requests
import sys
import time
import db_class
from threading import Timer

port = int(sys.argv[1])

app = FastAPI()

orquestrador = db_class.get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("sc1_volume", 0.0)
orquestrador.end_connection()


class Secador(BaseModel):
    quantidade: float


def regra_negocio(**kwargs):
    disponivel = kwargs["volume"]
    payload = {"qtde_biodiesel": disponivel}
    response = requests.post(
        f"http://127.0.0.1:{port+1}/tanque_etoh", json=payload)
    while response.status_code != 200:
        time.sleep(1)
        response = requests.post(
            f'http://127.0.0.1:{port+1}/tanque_etoh', json=payload)


@app.post("/secador_1")
def entrada_volume(volume: Secador):
    global orquestrador
    volume = volume.quantidade * 0.975
    tempo = 5*volume
    t = Timer(round(tempo, 2), regra_negocio, kwargs={"volume": volume})
    t.start()
    orquestrador.begin_connection()
    orquestrador.update("sc1_volume", volume)
    orquestrador.end_connection()
    return {"Volume adicionado": volume}


if __name__ == "__main__":
    uvicorn.run("secador_1:app", host="127.0.0.1",
                port=port, log_level="info", reload=True)
