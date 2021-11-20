"""decantador."""

import uvicorn
import sys
import requests
import db_class
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Timer
from time import sleep

tabela = db_class.SimpleDB("tabela_decantador",
                           volume_decantador=0.0)


class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float


app = FastAPI()


@app.get("/decantador/", status_code=200)
def obter_volume_tanque_lavagem_1():
    """Obtém o volume atual armazenado no tanque."""
    global tabela
    tabela.begin_connection()
    volume_decantador = tabela.get("volume_decantador")
    tabela.end_connection()
    return {"volume_decantador": volume_decantador}


@app.post("/decantador/", status_code=200)
def inserir_volume_tanque_lavagem_1(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque.

    - Armazena no máximo 10L
    """
    global tabela
    tabela.begin_connection()

    if (tanque.qtde_biodiesel > 0
       and tanque.qtde_biodiesel + tabela.get("volume_decantador") <= 10):
        tabela.increment("volume_decantador", tanque.qtde_biodiesel)
        print(f"RECV POST {tanque}")
        resposta = {"volume_decantador": tabela.get("volume_decantador")}
    else:
        response.status_code = 400
        resposta = {}

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

    stop_time = 0

    while True:
        if (stop_time > 0):
            sleep(stop_time)
            stop_time = 0
        else:
            sleep(1)

        if stop_thread is True:
            break

        tabela.begin_connection()
        volume_decantador = tabela.get("volume_decantador")

        if volume_decantador >= 6:
            result = 6
            tabela.increment("volume_decantador", -6)
        else:
            result = volume_decantador
            tabela.increment("volume_decantador", -result)

        tabela.print_table()
        tabela.end_connection()

        stop_time = result/3 * 5

        # requests.post(f"http://127.0.0.1:{int(sys.argv[1])+1}/tanque_glicerina",
        #               json={"qtde_biodiesel": result*0.03})
        # requests.post(f"http://127.0.0.1:{int(sys.argv[1])+2}/secador_1",
        #               json={"qtde_biodiesel": result*0.09})
        # requests.post(f"http://127.0.0.1:{int(sys.argv[1])+4}/tanque_lavagem_1",
        #               json={"qtde_biodiesel": result*0.88})


if __name__ == "__main__":
    global porta
    global stop_thread

    t = Timer(0, enviar_para_tanque_glicerina)
    t.start()
    stop_thread = False

    uvicorn.run("decantador:app", host="127.0.0.1", port=int(sys.argv[1]),
                log_level="info", reload=True)

    stop_thread = True
