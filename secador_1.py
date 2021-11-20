from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, requests, db_class
from threading import Timer

app = FastAPI()

class Secador(BaseModel):
    quantidade: float

def regra_negocio(**kwargs):
    disponivel = kwargs["volume"]
    # payload = {"Oleo" : disponivel }
    # response = requests.post("http://127.0.0.1:9999/tanque_etoh", json= payload )
    # while response.status_code != 200:
    #   time.sleep(1)
    #   response = requests.post(f'http://127.0.0.1:9999/tanque_etoh', json=payload)

@app.post("/")
def entrada_volume(volume: Secador ):
    volume = volume.quantidade
    tempo = 5*volume
    t = Timer(tempo, regra_negocio, kwargs={"volume":volume})
    t.start()
    return {"Volume adicionado": volume}

if __name__ == "__main__":
    uvicorn.run("secador_1:app", host="127.0.0.1", port=int(4444), log_level="info", reload=True)

