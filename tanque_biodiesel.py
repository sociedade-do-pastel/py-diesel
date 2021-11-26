import uvicorn, sys, db_class
from fastapi import FastAPI, Response
from pydantic import BaseModel
from datetime import datetime

# =========== Variáveis de controle ===========
volume_tanque_biodiesel = 0
# =============================================

orquestrador = db_class.get_db("orquestrador.db")
orquestrador.begin_connection()
orquestrador.insert("tb_qtde_biodiesel", 0.0)
orquestrador.end_connection()


class Tanque(BaseModel):
    qtde_biodiesel: float


app = FastAPI()


@app.get('/tanque_biodiesel/', status_code=200)
def obter_volume_tanque_biodiesel():
    global volume_tanque_biodiesel
    return {'volume_tanque_biodiesel': volume_tanque_biodiesel}


@app.post('/tanque_biodiesel/', status_code=200)
def inserir_volume_tanque_biodiesel(tanque: Tanque, response: Response):
    global volume_tanque_biodiesel, orquestrador
    if tanque.qtde_biodiesel > 0:
        volume_tanque_biodiesel += tanque.qtde_biodiesel
        orquestrador.begin_connection()
        orquestrador.update("tb_qtde_biodiesel", volume_tanque_biodiesel)
        data = datetime.now()
        print(f'{__name__} [{data.hour}:{data.minute}:{data.second}]: RECEBI {round(tanque.qtde_biodiesel, 3)} DE BIODIESEL')
        orquestrador.print_table()
        print()
        orquestrador.end_connection()
        return {'volume_tanque_biodiesel': volume_tanque_biodiesel}
    response.status_code = 400
    return {}


if __name__ == '__main__':
    uvicorn.run("tanque_biodiesel:app", host="127.0.0.1", port=int(
        sys.argv[1]), log_level="warning", reload=True)
