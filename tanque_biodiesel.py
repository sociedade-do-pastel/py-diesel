import uvicorn, sys
from fastapi import FastAPI, Response
from pydantic import BaseModel

#=========== Variáveis de controle ===========
volume_tanque_biodiesel = 0
#=============================================

class Tanque(BaseModel):
	qtde_biodiesel: float

app = FastAPI()

@app.get('/tanque_biodiesel/', status_code=200)
def obter_volume_tanque_biodiesel():
	global volume_tanque_biodiesel
	return {'volume_tanque_biodiesel': volume_tanque_biodiesel}

@app.post('/tanque_biodiesel/', status_code=200)
def inserir_volume_tanque_biodiesel(tanque: Tanque, response: Response):
	global volume_tanque_biodiesel
	if tanque.qtde_biodiesel > 0:
		volume_tanque_biodiesel += tanque.qtde_biodiesel
		return { 'volume_tanque_biodiesel': volume_tanque_biodiesel }
	response.status_code = 400
	return {}



if __name__ == '__main__':
	uvicorn.run("tanque_biodiesel:app", host="127.0.0.1", port=int(sys.argv[1]), log_level="critical", reload=True)