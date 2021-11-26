import uvicorn
import sys
import requests
import time
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Thread
from db_class import SimpleDB, get_db
from datetime import datetime


port = int(sys.argv[1])

tabela = SimpleDB("tanque_naoh_etoh", volume_etoh=0.0, volume_naoh=0.0)
orquestrador = get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("tne_qtde_etoh", 0.0)
orquestrador.insert("tne_qtde_naoh", 0.0)
orquestrador.end_connection()


def adiciona_volumes():
    global tabela, orquestrador

    while True:
        time.sleep(1)
        # begin connection
        tabela.begin_connection()
        orquestrador.begin_connection()
        # begin connection

        tabela.increment("volume_naoh", 0.25)
        tabela.increment("volume_etoh", 0.125)
        etoh = tabela.get("volume_etoh")
        naoh = tabela.get("volume_naoh")
        # table's end_connection
        tabela.end_connection()
        orquestrador.update("tne_qtde_naoh", naoh)
        orquestrador.update("tne_qtde_etoh", etoh)

        data = datetime.now()
        print(
            f'tanque_naoh_etoh [{data.hour}:{data.minute}:{data.second}]: RECEBI {0.125} DE EtOH E {0.25} DE NaOH')
        orquestrador.print_table()
        print()

        # end connection
        orquestrador.end_connection()


def envia_volumes():
    global tabela, orquestrador

    while True:
        time.sleep(1)
        tabela.begin_connection()
        volume_etoh = tabela.get("volume_etoh")
        volume_naoh = tabela.get("volume_naoh")
        tabela.end_connection()

        if volume_etoh > 0 or volume_naoh > 0:
            enviar_naoh, enviar_etoh = volume_naoh, volume_etoh
            if volume_naoh > 1:
                enviar_naoh = 1
            if volume_etoh > 1:
                enviar_etoh = 1

            response = requests.Response()
            try:
                response = requests.post(f'http://127.0.0.1:{port-5}/reator/naoh_etoh', json={
                    "qtde_naoh": enviar_naoh, "qtde_etoh": enviar_etoh})
            except Exception:
                pass

            while response.status_code != 200:
                try:
                    time.sleep(1)
                    response = requests.post(f'http://127.0.0.1:{port-5}/reator/naoh_etoh', json={
                        "qtde_naoh": enviar_naoh, "qtde_etoh": enviar_etoh})
                except Exception:
                    continue

            # begin connection
            orquestrador.begin_connection()
            tabela.begin_connection()
            # begin connection
            tabela.increment("volume_naoh", -enviar_naoh)
            tabela.increment("volume_etoh", -enviar_etoh)
            naoh = tabela.get("volume_naoh")
            etoh = tabela.get("volume_etoh")
            # end connection
            tabela.end_connection()

            orquestrador.update("tne_qtde_naoh", naoh)
            orquestrador.update("tne_qtde_etoh", etoh)
            orquestrador.end_connection()


class Tanque(BaseModel):
    qtde_etoh: float


app = FastAPI()


@app.post('/tanque_naoh_etoh/', status_code=200)
def inserir_volume_tanque_naoh_etoh(tanque: Tanque, response: Response):
    global tabela, orquestrador
    if tanque.qtde_etoh > 0:
        # begin connection
        tabela.begin_connection()
        orquestrador.begin_connection()
        # begin connection
        tabela.increment("volume_etoh", tanque.qtde_etoh)
        volume_etoh = tabela.get("volume_etoh")
        # end connection
        tabela.end_connection()
        orquestrador.update("tne_qtde_etoh", volume_etoh)
        data = datetime.now()
        print(
            f'tanque_naoh_etoh [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(tanque.qtde_etoh, 3)} DE EtOH')
        orquestrador.print_table()
        print()
        # end connection
        orquestrador.end_connection()
        # end connection
        return {'volume_etoh': volume_etoh}
    response.status_code = 400
    return {}


if __name__ == '__main__':
    t = Thread(target=adiciona_volumes, daemon=True)
    t.start()
    t1 = Thread(target=envia_volumes, daemon=True)
    t1.start()
    uvicorn.run("tanque_naoh_etoh:app", host="127.0.0.1",
                port=port, log_level="warning", reload=True)
