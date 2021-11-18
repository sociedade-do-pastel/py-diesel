import uvicorn
import sys
import threading
import time
import requests
from fastapi import FastAPI, Response
from pydantic import BaseModel
from db_class import SimpleDB


class Input_naoh_etoh(BaseModel):
    qtde_naoh: float
    qtde_etoh: float


class Input_oleo(BaseModel):
    qtde_oleo: float


MIN_ETOH = 2.5
MIN_NAOH = 1.25
MIN_OLEO = 1.25
PROD_INSUMO = 5.0
LIM_INSUMO = 6.0
REACTOR_PORT = 0
INTERVAL_BETWEEN_CHECKS = 1

database = SimpleDB("reator",
                    volume_oleo=0.0,
                    volume_naoh=0.0,
                    volume_etoh=0.0,
                    volume_insumo=0.0)


app = FastAPI()


try:
    REACTOR_PORT = int(sys.argv[1])
except IndexError:
    REACTOR_PORT = 6666

DECANTER_PORT = REACTOR_PORT + 1


def check_reactor():
    database.begin_connection()
    while True:
        temp_vol_etoh = database.get("volume_etoh")
        temp_vol_naoh = database.get("volume_naoh")
        temp_vol_oleo = database.get("volume_oleo")
        temp_vol_insumo = database.get("volume_insumo")

        if temp_vol_etoh >= MIN_ETOH and temp_vol_naoh >= MIN_NAOH and temp_vol_oleo >= MIN_OLEO:
            temp_vol_etoh -= MIN_ETOH
            temp_vol_naoh -= MIN_NAOH
            temp_vol_oleo -= MIN_OLEO
            temp_vol_insumo += PROD_INSUMO

            if (temp_vol_insumo >= LIM_INSUMO):
                valor_enviar = LIM_INSUMO
                temp_vol_insumo -= LIM_INSUMO
            else:
                valor_enviar = temp_vol_insumo
                temp_vol_insumo -= temp_vol_insumo

            if enviar_decantador(valor_enviar):
                database.update("volume_etoh", temp_vol_etoh)
                database.update("volume_naoh", temp_vol_naoh)
                database.update("volume_oleo", temp_vol_oleo)
                database.update("volume_insumo", temp_vol_insumo)
        time.sleep(INTERVAL_BETWEEN_CHECKS)
    database.end_connection()


def enviar_decantador(valor):
    sv_response = requests.post(f"http://127.0.0.1:{DECANTER_PORT}/decantador",
                                json={"volume_insumo": valor})

    return (sv_response.status_code == 200)


@app.post("/reator/oleo", status_code=200)
def inserir_oleo_reator(recv_oleo: Input_oleo, response: Response):
    global database
    try:
        database.begin_connection()
        if recv_oleo.qtde_oleo is not None and recv_oleo.qtde_oleo >= 0:
            database.increment("volume_oleo", recv_oleo.qtde_oleo)
            return {'volume_oleo': database.get('volume_oleo')}
    finally:
        database.end_connection()

    response.status_code = 400
    return dict()


@app.post("/reator/naoh_etoh", status_code=200)
def inserir_naoh_etoh_reator(recv_naoh_etoh: Input_naoh_etoh,
                             response: Response):
    global database
    try:
        database.begin_connection()
        if recv_naoh_etoh.qtde_etoh is not None and recv_naoh_etoh.qtde_naoh is not None:
            if recv_naoh_etoh.qtde_etoh >= 0:
                database.increment("volume_etoh", recv_naoh_etoh.qtde_etoh)
            if recv_naoh_etoh.qtde_naoh >= 0:
                database.increment("volume_naoh", recv_naoh_etoh.qtde_naoh)
            return {'volume_etoh': database.get('volume_etoh'),
                    'volume_naoh': database.get('volume_naoh')}
    finally:
        database.end_connection()

    response.status_code = 400
    return dict()


@app.get("/reator/", status_code=200)
def pegar_volume_reator():
    global database
    try:
        database.begin_connection()
        return {'volume_etoh': database.get('volume_etoh'),
                'volume_naoh': database.get('volume_naoh'),
                'volume_oleo': database.get('volume_oleo'),
                'volume_insumo': database.get('volume_insumo')}

    finally:
        database.end_connection()


if __name__ == '__main__':
    check_thread = threading.Thread(target=check_reactor, daemon=True)
    check_thread.start()
    uvicorn.run("reator:app", host="127.0.0.1",
                port=REACTOR_PORT, log_level="info", reload=True)
