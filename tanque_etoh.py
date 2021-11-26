"""tanque_etoh."""

import uvicorn, sys, requests
from fastapi import FastAPI, Response
from pydantic import BaseModel

port = int(sys.argv[1])

class Tanque(BaseModel):
    """BaseModel provê formato para json."""

    qtde_biodiesel: float

app = FastAPI()

@app.post("/tanque_etoh/", status_code=200)
def inserir_volume_tanque_etoh(tanque: Tanque, response: Response):
    """Insere uma quantidade no tanque."""
    if tanque.qtde_biodiesel > 0:
        requests.post(f"http://127.0.0.1:{port+1}/tanque_naoh_etoh",
                      json={"qtde_etoh": tanque.qtde_biodiesel})
        return {"volume_tanque_etoh": tanque.qtde_biodiesel}
    response.status_code = 400
    return {}

if __name__ == "__main__":
    uvicorn.run("tanque_etoh:app", host="127.0.0.1", port=port,
                log_level="critical", reload=True)
