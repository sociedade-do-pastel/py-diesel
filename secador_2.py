import uvicorn
import sys
import threading
import time
import requests
from math import floor
from fastapi import FastAPI, Response
from pydantic import BaseModel
from db_class import SimpleDB

try:
    DRYER_PORT = int(sys.argv[1])
except IndexError:
    DRYER_PORT = 6666

TANK_PORT = DRYER_PORT + 3
HOLD_DELAY = 5  # in seconds
DRYER_DEDUCTION = 0.025


app = FastAPI()
database = SimpleDB("secador_2", volume_secador=0.0)
hold = False

class Secador2(BaseModel):
    volume_secador_2: float


@app.post("/secador_2/", status_code=200)
def inserir_volume_secador(input_secador: Secador2, response: Response):
    global database
    global hold
    if input_secador.volume_secador_2 >= 0:
        discounted_input = (input_secador.volume_secador_2 -
                            input_secador.volume_secador_2 * DRYER_DEDUCTION)
        try:
            database.begin_connection()
            database.increment("volume_secador", discounted_input)
            hold = True
            return {"volume_secador_2": database.get("volume_secador")}
        finally:
            database.end_connection()
            
    response.status_code = 400
    return dict()


@app.get("/secador_2/", status_code=200)
def pegar_volume_secador():
    global database
    try:
        database.begin_connection()
        return {"volume_secador_2": database.get("volume_secador")}
    finally:
        database.end_connection()


def hold():
    global hold
    database.begin_connection()
    while True:
        liters = floor(database.get("volume_secador"))
        if (hold and liters > 0):
            time.sleep(liters * HOLD_DELAY)
            if enviar_litros(liters):
                database.increment("volume_secador", -liters)
            hold = False
    database.end_connection()


def enviar_litros(valor):
    sv_response = requests.post(                          
        f"http://127.0.0.1:{TANK_PORT}/tanque_biodiesel", 
        json={"volume_secador_2": valor})                 
    return (sv_response.status_code == 200)               


if __name__ == "__main__":
    hold_thread = threading.Thread(target=hold, daemon=True)
    hold_thread.start()
    uvicorn.run("secador_2:app", host="127.0.0.1",
                port=DRYER_PORT, log_level="info", reload=True)
