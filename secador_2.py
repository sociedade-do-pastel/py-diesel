from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn, requests, sys, time
from threading import Timer

port = int(sys.argv[1])

app = FastAPI()

class Secador(BaseModel):
    quantidade: float

def regra_negocio(**kwargs):
    disponivel = kwargs["volume"]
    payload = {"qtde_biodiesel" : disponivel }
    response = requests.post(f"http://127.0.0.1:{port+1}/tanque_biodiesel", json=payload)
    while response.status_code != 200:
      time.sleep(1)
      response = requests.post(f'http://127.0.0.1:{port+1}/tanque_biodiesel', json=payload)

@app.post("/secador_2")
def entrada_volume(volume: Secador):
    volume = volume.quantidade * 0.975
    tempo = 5*volume
    t = Timer(tempo, regra_negocio, kwargs={"volume":volume})
    t.start()
    return {"Volume adicionado": volume}

if __name__ == "__main__":
    uvicorn.run("secador_2:app", host="127.0.0.1", port=port, log_level="critical", reload=True)
