"""decantador."""

import uvicorn, sys, requests, db_class
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Timer
from time import sleep
from datetime import datetime

port = int(sys.argv[1])

tabela = db_class.SimpleDB("tabela_decantador",
                           volume_decantador=0.0)
orquestrador = db_class.get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("dc_volume", 0.0)
orquestrador.end_connection()


class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float


app = FastAPI()


@app.post("/decantador/", status_code=200)
def inserir_volume_decantador(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque.

    - Armazena no máximo 10L
    """
    global tabela, orquestrador
    tabela.begin_connection()
    orquestrador.begin_connection()

    if (tanque.qtde_biodiesel > 0
            and tanque.qtde_biodiesel + (volume_atual := tabela.get("volume_decantador")) <= 10):

        tabela.update("volume_decantador", volume_atual + tanque.qtde_biodiesel)
        orquestrador.update("dc_volume", volume_atual + tanque.qtde_biodiesel)
        resposta = {"volume_decantador": volume_atual + tanque.qtde_biodiesel}

        data = datetime.now()
        print(f'{__name__} [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(tanque.qtde_biodiesel, 3)} LITROS DE INSUMO')
        orquestrador.print_table()
        print()

    else:
        response.status_code = 400
        resposta = {}

    orquestrador.end_connection()
    tabela.end_connection()
    return resposta


def enviar_para_tanque_glicerina():
    """Enviar até 6 L/s.

    - 3%  pro tanque_glicerina
    - 9%  pro secador_1
    - 88% pro tanque_lavagem_1

    Fica em espera por 5 segundos a cada 3L enviados.
    """
    global stop_thread
    global tabela
    global decantador

    stop_time = 0

    while True:
        if (stop_time > 0):
            sleep(stop_time)
            stop_time = 0
        else:
            sleep(1)

        if stop_thread is True:
            break

        orquestrador.begin_connection()
        tabela.begin_connection()

        volume_decantador = tabela.get("volume_decantador")

        if volume_decantador >= 3:
            result = 3
            tabela.update("volume_decantador", volume_decantador - 3)
            orquestrador.update("dc_volume", volume_decantador - 3)
        else:
            result = volume_decantador
            tabela.update("volume_decantador", volume_decantador - volume_decantador)
            orquestrador.update("dc_volume", volume_decantador - volume_decantador)

        tabela.end_connection()
        orquestrador.end_connection()

        stop_time = 0 if result == 0 else 5

        if result > 0:
            requests.post(f"http://127.0.0.1:{port+1}/tanque_glicerina",
                          json={"qtde_glicerina": result*0.03})
            requests.post(f"http://127.0.0.1:{port+2}/secador_1",
                          json={"quantidade": result*0.09})
            requests.post(f"http://127.0.0.1:{port+5}/tanque_lavagem_1",
                          json={"qtde_biodiesel": result*0.88})


if __name__ == "__main__":
    global stop_thread

    t = Timer(0, enviar_para_tanque_glicerina)
    t.start()
    stop_thread = False

    uvicorn.run("decantador:app", host="127.0.0.1", port=port,
                log_level="warning", reload=True)

    stop_thread = True
