"""tanque_etoh."""

import uvicorn
import sys
import requests
from fastapi import FastAPI, Response
from pydantic import BaseModel


class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float


app = FastAPI()


@app.get("/tanque_etoh/", status_code=200)
def obter_volume_tanque_etoh():
    """Obtém o volume atual armazenado no tanque."""
    global volume_tanque_etoh
    return {"volume_tanque_etoh": volume_tanque_etoh}


@app.post("/tanque_etoh/", status_code=200)
def inserir_volume_tanque_etoh(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque."""
    if tanque.qtde_biodiesel > 0:
        print(f"RECV POST {tanque}")
        requests.post(f"http://127.0.0.1:{int(sys.argv[1])+5}"
                      "/tanque_naoh_etoh", json=tanque)
        return {"volume_tanque_etoh": volume_tanque_etoh}
    response.status_code = 400
    return {}


if __name__ == "__main__":
    uvicorn.run("tanque_etoh:app", host="127.0.0.1", port=int(sys.argv[1]),
                log_level="info", reload=True)
