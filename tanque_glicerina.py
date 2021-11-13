import uvicorn, sys
from fastapi import FastAPI, Response
from pydantic import BaseModel

#=========== Variáveis de controle ===========
volume_tanque_glicerina = 0
#=============================================

class Tanque(BaseModel):
	qtde_glicerina: float

app = FastAPI()

@app.get('/tanque_glicerina/', status_code=200)
def obter_volume_tanque_glicerina():
	global volume_tanque_glicerina
	return {'volume_tanque_glicerina': volume_tanque_glicerina}

@app.post('/tanque_glicerina/', status_code=200)
def inserir_volume_tanque_glicerina(tanque: Tanque, response: Response):
	global volume_tanque_glicerina
	if tanque.qtde_glicerina > 0:
		volume_tanque_glicerina += tanque.qtde_glicerina
		print(f'RECV POST {tanque}')
		return { 'volume_tanque_glicerina': volume_tanque_glicerina }
	response.status_code = 400
	return {}



if __name__ == '__main__':
	uvicorn.run("tanque_glicerina:app", host="127.0.0.1", port=int(sys.argv[1]), log_level="info", reload=True)