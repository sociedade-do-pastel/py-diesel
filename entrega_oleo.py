import random
import requests
import sys
import time


if __name__ == '__main__':
    port = int(sys.argv[1]) + 1

    while 1:
        payload = {
            'quantidade': round(random.uniform(1.0, 2.0), 3)
        }
        response = requests.Response()

        try:
            response = requests.post(
                f'http://127.0.0.1:{port}/tanque_oleo', json=payload)
        except Exception:
            pass

        while response.status_code != 200:
            time.sleep(1)
            try:
                response = requests.post(
                    f'http://127.0.0.1:{port}/tanque_oleo', json=payload)
            except Exception:
                continue

        time.sleep(10)
