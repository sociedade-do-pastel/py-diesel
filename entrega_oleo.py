import random, requests, sys, time

if __name__ == '__main__':
	port = int(sys.argv[1]) + 1
	while 1:
		payload = {
			'quantidade': random.uniform(1.0, 2.0)
		}
		response = requests.post(f'http://127.0.0.1:{port}/tanque_oleo', json=payload)
		while response.status_code != 200:
			time.sleep(1)
			response = requests.post(f'http://127.0.0.1:{port}/tanque_oleo', json=payload)
		time.sleep(10)
