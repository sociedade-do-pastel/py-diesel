import uvicorn, sys, requests
from fastapi import FastAPI, Response
from pydantic import BaseModel
from threading import Timer
from db_class import SimpleDB

tabela = SimpleDB("tanque_naoh_etoh", volume_etoh=0.0, volume_naoh=0.0)

def adiciona_volumes():
	global tabela
	tabela.begin_connection()
	tabela.increment("volume_naoh", 0.25)
	tabela.increment("volume_etoh", 0.125)
	volume_naoh = tabela.get("volume_naoh")
	volume_etoh = tabela.get("volume_etoh")
	tabela.end_connection()
	t = Timer(1, adiciona_volumes)
	t.start()

def envia_volumes():
	global tabela

	tabela.begin_connection()
	volume_etoh = tabela.get("volume_etoh")
	volume_naoh = tabela.get("volume_naoh")
	tabela.end_connection()

	if volume_etoh > 0 or volume_naoh > 0:
		enviar_naoh, enviar_etoh = volume_naoh, volume_etoh
		if volume_naoh > 1:
			enviar_naoh = 1
		if volume_etoh > 1:
			enviar_etoh = 1

		response = requests.post(f'http://127.0.0.1:{int(sys.argv[1]) - 9}/reator', json={ "qtde_naoh": enviar_naoh, "qtde_etoh": enviar_etoh })
		while response.status_code != 200:
			time.sleep(1)
			response = requests.post(f'http://127.0.0.1:{int(sys.argv[1]) - 9}/reator', json={ "qtde_naoh": enviar_naoh, "qtde_etoh": enviar_etoh })

		tabela.begin_connection()
		tabela.increment("volume_naoh", -enviar_naoh)
		tabela.increment("volume_etoh", -enviar_etoh)
		tabela.end_connection()

	t = Timer(1, envia_volumes)
	t.start()

class Tanque(BaseModel):
	qtde_etoh: float

app = FastAPI()


@app.post('/tanque_naoh_etoh/', status_code=200)
def inserir_volume_tanque_naoh_etoh(tanque: Tanque, response: Response):
	global tabela
	if tanque.qtde_etoh > 0:
		tabela.begin_connection()
		tabela.increment("volume_etoh", tanque.qtde_etoh)
		volume_etoh = tabela.get("volume_etoh")
		tabela.end_connection()
		return { 'volume_etoh': volume_etoh }
	response.status_code = 400
	return {}


if __name__ == '__main__':
	t = Timer(1, adiciona_volumes)
	t.start()
	t1 = Timer(1, envia_volumes)
	t1.start()
	uvicorn.run("tanque_naoh_etoh:app", host="127.0.0.1", port=int(sys.argv[1]), log_level="info", reload=True)