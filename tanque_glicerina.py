import uvicorn
import sys
from fastapi import FastAPI, Response
from pydantic import BaseModel
import db_class

# =========== Variáveis de controle ===========
volume_tanque_glicerina = 0
# =============================================

orquestrador = db_class.get_db("orquestrador.db")
orquestrador.begin_connection()
orquestrador.insert("tg_qtde_glicerina", 0.0)
orquestrador.end_connection()


class Tanque(BaseModel):
    qtde_glicerina: float


app = FastAPI()


@app.get('/tanque_glicerina/', status_code=200)
def obter_volume_tanque_glicerina():
    return {'volume_tanque_glicerina': volume_tanque_glicerina}


@app.post('/tanque_glicerina/', status_code=200)
def inserir_volume_tanque_glicerina(tanque: Tanque, response: Response):
    global volume_tanque_glicerina, orquestrador
    if tanque.qtde_glicerina > 0:
        volume_tanque_glicerina += tanque.qtde_glicerina
        orquestrador.begin_connection()
        orquestrador.update("tg_qtde_glicerina", volume_tanque_glicerina)
        orquestrador.end_connection()
        return {'volume_tanque_glicerina': volume_tanque_glicerina}
    response.status_code = 400
    return {}


if __name__ == '__main__':
    uvicorn.run("tanque_glicerina:app", host="127.0.0.1", port=int(
        sys.argv[1]), log_level="critical", reload=True)
