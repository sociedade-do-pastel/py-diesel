"""tanque_lavagem_1."""

import uvicorn, sys, requests, db_class
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Timer
from time import sleep
from datetime import datetime

porta = int(sys.argv[1])

tabela = db_class.SimpleDB("tabela_tanque_lavagem_1",
                           volume_tanque_lavagem_1=0.0)
orquestrador = db_class.get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("lv1_volume", 0.0)
orquestrador.end_connection()


class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float


app = FastAPI()


@app.post("/tanque_lavagem_1/", status_code=200)
def inserir_volume_tanque_lavagem_1(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque."""
    global tabela, orquestrador
    orquestrador.begin_connection()
    tabela.begin_connection()

    if tanque.qtde_biodiesel > 0:
        tabela.increment("volume_tanque_lavagem_1",
                         tanque.qtde_biodiesel*0.905)

        lv1_volume = tabela.get("volume_tanque_lavagem_1")
        orquestrador.update("lv1_volume", lv1_volume)
        data = datetime.now()
        print(f'{__name__} [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(tanque.qtde_biodiesel, 3)} DE BIODIESEL')
        orquestrador.print_table()
        print()
        resposta = {"volume_tanque_lavagem_1":
                    lv1_volume}
    else:
        response.status_code = 400
        resposta = {}

    tabela.end_connection()
    orquestrador.end_connection()
    return resposta


def enviar_para_tanque_lavagem_2():
    """Enviar 1.5 L/s para tanque_lavagem_2."""
    global stop_thread
    global tabela, orquestrador

    while True:
        sleep(1)

        if stop_thread is True:
            break

        tabela.begin_connection()
        volume_tanque_lavagem_1 = tabela.get("volume_tanque_lavagem_1")
        if volume_tanque_lavagem_1 >= 1.5:
            enviar = 1.5
            volume_tanque_lavagem_1 -= 1.5
        elif volume_tanque_lavagem_1 > 0:
            enviar = volume_tanque_lavagem_1
            volume_tanque_lavagem_1 = 0
        else:
            enviar = 0

        tabela.update("volume_tanque_lavagem_1", volume_tanque_lavagem_1)
        tabela.end_connection()

        orquestrador.begin_connection()
        orquestrador.update("lv1_volume", volume_tanque_lavagem_1)
        orquestrador.end_connection()

        if enviar != 0:
            requests.post(f"http://127.0.0.1:{porta+1}/tanque_lavagem_2",
                          json={"qtde_biodiesel": enviar})


if __name__ == "__main__":
    global stop_thread

    t = Timer(0, enviar_para_tanque_lavagem_2)
    t.start()
    stop_thread = False

    uvicorn.run("tanque_lavagem_1:app", host="127.0.0.1", port=porta,
                log_level="warning", reload=True)

    stop_thread = True
