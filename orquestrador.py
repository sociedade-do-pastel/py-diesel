import os, subprocess, sys, random, time

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

a = random.randint(8000, 60000)

subprocess.Popen([sys.executable, arquivos[8], str(a+8)])		# tanque_lavagem_1
subprocess.Popen([sys.executable, arquivos[9], str(a+9)])		# tanque_lavagem_2
subprocess.Popen([sys.executable, arquivos[10], str(a+10)])		# tanque_lavagem_3
subprocess.Popen([sys.executable, arquivos[1], str(a+1)])		# tanque_oleo
subprocess.Popen([sys.executable, arquivos[6], str(a+6)])		# tanque_etoh 
subprocess.Popen([sys.executable, arquivos[4], str(a+4)])		# tanque_glicerina
subprocess.Popen([sys.executable, arquivos[12], str(a+12)])		# tanque_biodiesel
subprocess.Popen([sys.executable, arquivos[5], str(a+5)])		# secador_1
subprocess.Popen([sys.executable, arquivos[11], str(a+11)])		# secador_2
subprocess.Popen([sys.executable, arquivos[2], str(a+2)])		# reator
subprocess.Popen([sys.executable, arquivos[3], str(a+3)])		# decantador
subprocess.Popen([sys.executable, arquivos[7], str(a+7)])		# tanque_naoh_etoh
# time.sleep(2)
subprocess.Popen([sys.executable, arquivos[0], str(a)])			# entrega_oleo

