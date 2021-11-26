import os
import subprocess
import sys
import random
import time
from db_class import SimpleDB


arquivos = [
    os.path.abspath('./entrega_oleo.py'),			# 8000
    os.path.abspath('./tanque_oleo.py'),			# 8001
    os.path.abspath('./reator.py'),					# 8002
    os.path.abspath('./decantador.py'),				# 8003
    os.path.abspath('./tanque_glicerina.py'),		# 8004
    os.path.abspath('./secador_1.py'),				# 8005
    os.path.abspath('./tanque_etoh.py'),			# 8006
    os.path.abspath('./tanque_naoh_etoh.py'),		# 8007
    os.path.abspath('./tanque_lavagem_1.py'),
    os.path.abspath('./tanque_lavagem_2.py'),
    os.path.abspath('./tanque_lavagem_3.py'),
    os.path.abspath('./secador_2.py'),
    os.path.abspath('./tanque_biodiesel.py')
]

database = SimpleDB("orquestrador")

a = random.randint(8000, 60000)

p1 = subprocess.Popen([sys.executable, arquivos[8], str(a+8)])		# tanque_lavagem_1
p2 = subprocess.Popen([sys.executable, arquivos[9], str(a+9)])		# tanque_lavagem_2
p3 = subprocess.Popen([sys.executable, arquivos[10], str(a+10)])	# tanque_lavagem_3
p4 = subprocess.Popen([sys.executable, arquivos[1], str(a+1)])		# tanque_oleo
p5 = subprocess.Popen([sys.executable, arquivos[6], str(a+6)])		# tanque_etoh
p6 = subprocess.Popen([sys.executable, arquivos[4], str(a+4)])		# tanque_glicerina
p7 = subprocess.Popen([sys.executable, arquivos[12], str(a+12)])	# tanque_biodiesel
p8 = subprocess.Popen([sys.executable, arquivos[5], str(a+5)])		# secador_1
p9 = subprocess.Popen([sys.executable, arquivos[11], str(a+11)])	# secador_2
p10 = subprocess.Popen([sys.executable, arquivos[2], str(a+2)])		# reator
p11 = subprocess.Popen([sys.executable, arquivos[3], str(a+3)])		# decantador
p12 = subprocess.Popen([sys.executable, arquivos[7], str(a+7)])		# tanque_naoh_etoh
p13 = subprocess.Popen([sys.executable, arquivos[0], str(a)])		# entrega_oleo

try:
    while True:
        pass
        # database.begin_connection()
        # database.print_table()
        # database.end_connection()
        # time.sleep(1)
except KeyboardInterrupt:
    p12.kill()
    p4.kill()
