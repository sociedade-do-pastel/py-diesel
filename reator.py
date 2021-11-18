import uvicorn
import sys
import threading
import time
import requests
from fastapi import FastAPI, Response
from pydantic import BaseModel
from db_class import SimpleDB


class Reator(BaseModel):
    qtde_oleo: float
    qtde_naoh: float
    qtd_etoh: float


REACTOR_PORT = 0
INTERVAL_BETWEEN_CHECKS = 60
database = SimpleDB(__file__,
                    volume_oleo=0.0,
                    volume_naoh=0.0,
                    volume_etoh=0.0,
                    volume_insumo=0.0)
MIN_ETOH = 2.5
MIN_NAOH = 1.25
MIN_OLEO = 1.25
PROD_INSUMO = 5.0
LIM_INSUMO = 6.0

app = FastAPI()


try:
    REACTOR_PORT = int(sys.argv[1])
except IndexError:
    REACTOR_PORT = 6666


def check_reactor():
    database.begin_connection()
    while True:
        temp_vol_etoh = database.get("volume_etoh")
        temp_vol_naoh = database.get("volume_naoh")
        temp_vol_oleo = database.get("volume_oleo")
        temp_vol_insumo = database.get("volume_insumo")

        if (temp_vol_etoh >= MIN_ETOH
            and temp_vol_naoh >= MIN_NAOH
                and temp_vol_oleo >= MIN_OLEO):
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

            enviar_decantador(valor_enviar)
            database.update("volume_etoh", temp_vol_etoh)
            database.update("volume_naoh", temp_vol_naoh)
            database.update("volume_oleo", temp_vol_oleo)
            database.update("volume_insumo", temp_vol_insumo)

        time.sleep(INTERVAL_BETWEEN_CHECKS)
    database.end_connection()


def enviar_decantador(valor):
    print(f'Valor enviado: {valor}')
    # requests.post()


@app.post("/reator/", status_code=200)
def inserir_volume_reator(reator: Reator, response: Response):

    response.status_code = 400
    return dict()


if __name__ == '__main__':
    check_thread = threading.Thread(check_reactor)
    uvicorn.run("reator:app", host="127.0.0.1",
                port=REACTOR_PORT, log_level="info", reload=True)
