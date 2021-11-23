"""tanque_lavagem_3."""
#  baseado no modelo de tanque de lavagem de @Guior (Guilherme Ormond)
import uvicorn
import sys
import requests
import db_class
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Timer
from time import sleep

porta = int(sys.argv[1])

tabela = db_class.SimpleDB("tabela_tanque_lavagem_3",
                           volume_tanque_lavagem_3=0.0)

orquestrador = db_class.get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("lv3_volume", 0.0)
orquestrador.end_connection()


class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float


app = FastAPI()


@app.post("/tanque_lavagem_3/", status_code=200)
def inserir_volume_tanque_lavagem_3(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque."""
    global tabela, orquestrador
    tabela.begin_connection()
    orquestrador.begin_connection()
    if tanque.qtde_biodiesel > 0:
        tabela.increment("volume_tanque_lavagem_3",
                         tanque.qtde_biodiesel*0.905)
        orquestrador.increment("lv3_volume",
                               tanque.qtde_biodiesel*0.905)
        resposta = {"volume_tanque_lavagem_3":
                    tabela.get("volume_tanque_lavagem_3")}
    else:
        response.status_code = 400
        resposta = {}

    tabela.end_connection()
    orquestrador.end_connection()
    return resposta


def enviar_para_secador_2():
    """Enviar 1.5 L/s para secador_2."""
    global stop_thread
    global tabela, orquestrador

    while True:
        sleep(1)

        if stop_thread is True:
            break

        tabela.begin_connection()
        volume_tanque_lavagem_3 = tabela.get("volume_tanque_lavagem_3")
        if volume_tanque_lavagem_3 >= 1.5:
            enviar = 1.5
            volume_tanque_lavagem_3 -= 1.5
        elif volume_tanque_lavagem_3 > 0:
            enviar = volume_tanque_lavagem_3
            volume_tanque_lavagem_3 = 0
        else:
            enviar = 0

        tabela.update("volume_tanque_lavagem_3", volume_tanque_lavagem_3)
        orquestrador.begin_connection()
        orquestrador.update("lv3_volume", volume_tanque_lavagem_3)
        tabela.end_connection()
        orquestrador.end_connection()

        if enviar != 0:
            requests.post(f"http://127.0.0.1:{porta+1}/secador_2",
                          json={"quantidade": enviar})


if __name__ == "__main__":
    global stop_thread

    t = Timer(0, enviar_para_secador_2)
    t.start()
    stop_thread = False

    uvicorn.run("tanque_lavagem_3:app", host="127.0.0.1", port=porta,
                log_level="info", reload=True)

    stop_thread = True
