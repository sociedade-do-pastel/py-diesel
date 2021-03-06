import uvicorn
import requests
import sys
import time
import db_class
from fastapi import FastAPI
from pydantic import BaseModel
from threading import Timer
from datetime import datetime

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
    orquestrador.begin_connection()
    volume_atual = orquestrador.get("sc1_volume")
    orquestrador.update("sc1_volume", volume_atual - disponivel)
    orquestrador.end_connection()


@app.post("/secador_1")
def entrada_volume(volume: Secador):
    global orquestrador
    volume_og = volume
    volume = volume.quantidade * 0.975
    tempo = 5*volume

    orquestrador.begin_connection()
    volume_atual = orquestrador.get("sc1_volume")
    orquestrador.update("sc1_volume", volume + volume_atual)

    data = datetime.now()
    print(
        f'{__name__} [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(volume_og.quantidade, 3)} DE EtOH')
    orquestrador.print_table()
    print()
    orquestrador.end_connection()

    t = Timer(round(tempo, 2), regra_negocio, kwargs={"volume": volume})
    t.start()
    return {"Volume adicionado": volume + volume_atual}


if __name__ == "__main__":
    uvicorn.run("secador_1:app", host="127.0.0.1",
                port=port, log_level="warning", reload=True)
