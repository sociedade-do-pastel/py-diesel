"""tanque_lavagem_2."""

import uvicorn, sys, requests, db_class
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Timer
from time import sleep
from datetime import datetime

porta = int(sys.argv[1])

tabela = db_class.SimpleDB("tabela_tanque_lavagem_2",
                           volume_tanque_lavagem_2=0.0)
orquestrador = db_class.get_db("orquestrador.db")

orquestrador.begin_connection()
orquestrador.insert("lv2_volume", 0.0)
orquestrador.end_connection()


class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float


app = FastAPI()


@app.post("/tanque_lavagem_2/", status_code=200)
def inserir_volume_tanque_lavagem_2(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque."""
    global tabela, orquestrador

    tabela.begin_connection()
    orquestrador.begin_connection()

    if tanque.qtde_biodiesel > 0:
        tabela.increment("volume_tanque_lavagem_2",
                         tanque.qtde_biodiesel*0.905)

        lv2_volume = tabela.get("volume_tanque_lavagem_2")
        orquestrador.update("lv2_volume",
                            lv2_volume)
        data = datetime.now()
        print(f'{__name__} [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(tanque.qtde_biodiesel, 3)} DE BIODIESEL')
        orquestrador.print_table()
        print()
        resposta = {"volume_tanque_lavagem_2":
                    lv2_volume}
    else:
        response.status_code = 400
        resposta = {}

    tabela.end_connection()
    orquestrador.end_connection()
    return resposta


def enviar_para_tanque_lavagem_3():
    """Enviar 1.5 L/s para tanque_lavagem_3."""
    global stop_thread
    global tabela

    while True:
        sleep(1)

        if stop_thread is True:
            break

        tabela.begin_connection()
        volume_tanque_lavagem_2 = tabela.get("volume_tanque_lavagem_2")
        if volume_tanque_lavagem_2 >= 1.5:
            enviar = 1.5
            volume_tanque_lavagem_2 -= 1.5
        elif volume_tanque_lavagem_2 > 0:
            enviar = volume_tanque_lavagem_2
            volume_tanque_lavagem_2 = 0
        else:
            enviar = 0

        tabela.update("volume_tanque_lavagem_2", volume_tanque_lavagem_2)
        tabela.end_connection()

        orquestrador.begin_connection()
        orquestrador.update("lv2_volume", volume_tanque_lavagem_2)
        orquestrador.end_connection()

        if enviar != 0:
            requests.post(f"http://127.0.0.1:{porta+1}/tanque_lavagem_3",
                          json={"qtde_biodiesel": enviar})


if __name__ == "__main__":
    global stop_thread

    t = Timer(0, enviar_para_tanque_lavagem_3)
    t.start()
    stop_thread = False

    uvicorn.run("tanque_lavagem_2:app", host="127.0.0.1", port=porta,
                log_level="warning", reload=True)

    stop_thread = True
