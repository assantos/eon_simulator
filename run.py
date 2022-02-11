#!/usr/bin/env python
# -*- coding: utf-8 -*-

from eon_simulador import Simulador
import simpy
from random import *
from config import *
import numpy as np

def CalculaIntervalo(amostra):
	# calcula média e intervalo de confiança de uma amostra (t de Student) 95%. 
	media = np.mean(amostra)
	desvio = np.std(amostra, ddof=1)
	intervalo = (desvio/len(amostra))*1.833
	return [media,intervalo]

def main(args):
	topologia = TOPOLOGY
	arquivo1  = open('out/'+topologia+'/bloqueio'+'.dat', 'w')
	arquivo2  = open('out/'+topologia+'/bloqueio_10'+'.dat', 'w')
	arquivo3  = open('out/'+topologia+'/bloqueio_20'+'.dat', 'w')
	arquivo4  = open('out/'+topologia+'/bloqueio_40'+'.dat', 'w')
	arquivo5  = open('out/'+topologia+'/bloqueio_80'+'.dat', 'w')
	arquivo6  = open('out/'+topologia+'/bloqueio_160'+'.dat', 'w')
	arquivo7  = open('out/'+topologia+'/bloqueio_200'+'.dat', 'w')
	arquivo8  = open('out/'+topologia+'/bloqueio_400'+'.dat', 'w')
	arquivo9  = open('out/'+topologia+'/bloqueio_classe1'+'.dat', 'w')
	arquivo10  = open('out/'+topologia+'/bloqueio_classe2'+'.dat', 'w')
	arquivo11  = open('out/'+topologia+'/bloqueio_classe3'+'.dat', 'w')
	arquivo12  = open('out/'+topologia+'/bloqueio_banda'+'.dat', 'w')

	for e in range(ERLANG_MIN, ERLANG_MAX+1, ERLANG_INC):
		Bloqueio = []
		Bloqueio_10 = []
		Bloqueio_20 = []
		Bloqueio_40 = []
		Bloqueio_80 = []
		Bloqueio_160 = []
		Bloqueio_200 = []
		Bloqueio_400 = []
		Bloqueio_classe1 = []
		Bloqueio_classe2 = []
		Bloqueio_classe3 = []
		Bloqueio_banda = []

		for rep in range(10):
			rate = e / HOLDING_TIME
			seed(RANDOM_SEED[rep])
			env = simpy.Environment()
			simulador = Simulador(env)
			env.process(simulador.Run(rate))
			env.run()
			print("Erlang", e, "Simulacao...", rep)
			print("bloqueadas", simulador.NumReqBlocked, "de", NUM_OF_REQUESTS)
			Bloqueio.append(simulador.NumReqBlocked / float(NUM_OF_REQUESTS))
			Bloqueio_10.append(simulador.NumReqBlocked_10/float(simulador.NumReq_10))
			Bloqueio_20.append(simulador.NumReqBlocked_20/float(simulador.NumReq_20))
			Bloqueio_40.append(simulador.NumReqBlocked_40/float(simulador.NumReq_40))
			Bloqueio_80.append(simulador.NumReqBlocked_80/float(simulador.NumReq_80))
			Bloqueio_160.append(simulador.NumReqBlocked_160/float(simulador.NumReq_160))
			Bloqueio_200.append(simulador.NumReqBlocked_200/float(simulador.NumReq_200))
			Bloqueio_400.append(simulador.NumReqBlocked_400/float(simulador.NumReq_400))
			Bloqueio_classe1.append(simulador.NumReqBlocked_classe1/float(simulador.NumReq_classe1))
			Bloqueio_classe2.append(simulador.NumReqBlocked_classe2/float(simulador.NumReq_classe2))
			Bloqueio_classe3.append(simulador.NumReqBlocked_classe3/float(simulador.NumReq_classe3))
			BD_solicitada = ((simulador.NumReq_10)*10+(simulador.NumReq_20)*20+(simulador.NumReq_40)*40+(simulador.NumReq_80)*80+(simulador.NumReq_160)*160+(simulador.NumReq_200)*200+(simulador.NumReq_400)*400)
			BD_bloqueada = ((simulador.NumReqBlocked_10)*10+(simulador.NumReqBlocked_20)*20+(simulador.NumReqBlocked_40)*40+(simulador.NumReqBlocked_80)*80+(simulador.NumReqBlocked_160)*160+(simulador.NumReqBlocked_200)*200+(simulador.NumReqBlocked_400)*400)
			Bloqueio_banda.append(BD_bloqueada/float(BD_solicitada))

		intervalo = CalculaIntervalo(Bloqueio)
		intervalo_10 = CalculaIntervalo(Bloqueio_10)
		intervalo_20 = CalculaIntervalo(Bloqueio_20)
		intervalo_40 = CalculaIntervalo(Bloqueio_40)
		intervalo_80 = CalculaIntervalo(Bloqueio_80)
		intervalo_160 = CalculaIntervalo(Bloqueio_160)
		intervalo_200 = CalculaIntervalo(Bloqueio_200)
		intervalo_400 = CalculaIntervalo(Bloqueio_400)
		intervalo_classe1 = CalculaIntervalo(Bloqueio_classe1)
		intervalo_classe2 = CalculaIntervalo(Bloqueio_classe2)
		intervalo_classe3 = CalculaIntervalo(Bloqueio_classe3)
		intervalo_bloqueio_banda = CalculaIntervalo(Bloqueio_banda)

		arquivo1.write(str(e))
		arquivo1.write("\t")
		arquivo1.write(str(intervalo[0]))
		arquivo1.write("\t")
		arquivo1.write(str(intervalo[0]-intervalo[1]))
		arquivo1.write("\t")
		arquivo1.write(str(intervalo[0]+intervalo[1]))
		arquivo1.write("\n")

		arquivo2.write(str(e))
		arquivo2.write("\t")
		arquivo2.write(str(intervalo_10[0]))
		arquivo2.write("\t")
		arquivo2.write(str(intervalo_10[0]-intervalo_10[1]))
		arquivo2.write("\t")
		arquivo2.write(str(intervalo_10[0]+intervalo_10[1]))
		arquivo2.write("\n")

		arquivo3.write(str(e))
		arquivo3.write("\t")
		arquivo3.write(str(intervalo_20[0]))
		arquivo3.write("\t")
		arquivo3.write(str(intervalo_20[0]-intervalo_20[1]))
		arquivo3.write("\t")
		arquivo3.write(str(intervalo_20[0]+intervalo_20[1]))
		arquivo3.write("\n")

		arquivo4.write(str(e))
		arquivo4.write("\t")
		arquivo4.write(str(intervalo_40[0]))
		arquivo4.write("\t")
		arquivo4.write(str(intervalo_40[0]-intervalo_40[1]))
		arquivo4.write("\t")
		arquivo4.write(str(intervalo_40[0]+intervalo_40[1]))
		arquivo4.write("\n")

		arquivo5.write(str(e))
		arquivo5.write("\t")
		arquivo5.write(str(intervalo_80[0]))
		arquivo5.write("\t")
		arquivo5.write(str(intervalo_80[0]-intervalo_80[1]))
		arquivo5.write("\t")
		arquivo5.write(str(intervalo_80[0]+intervalo_80[1]))
		arquivo5.write("\n")

		arquivo6.write(str(e))
		arquivo6.write("\t")
		arquivo6.write(str(intervalo_160[0]))
		arquivo6.write("\t")
		arquivo6.write(str(intervalo_160[0]-intervalo_160[1]))
		arquivo6.write("\t")
		arquivo6.write(str(intervalo_160[0]+intervalo_160[1]))
		arquivo6.write("\n")

		arquivo7.write(str(e))
		arquivo7.write("\t")
		arquivo7.write(str(intervalo_200[0]))
		arquivo7.write("\t")
		arquivo7.write(str(intervalo_200[0]-intervalo_200[1]))
		arquivo7.write("\t")
		arquivo7.write(str(intervalo_200[0]+intervalo_200[1]))
		arquivo7.write("\n")

		arquivo8.write(str(e))
		arquivo8.write("\t")
		arquivo8.write(str(intervalo_400[0]))
		arquivo8.write("\t")
		arquivo8.write(str(intervalo_400[0]-intervalo_400[1]))
		arquivo8.write("\t")
		arquivo8.write(str(intervalo_400[0]+intervalo_400[1]))
		arquivo8.write("\n")

		arquivo9.write(str(e))
		arquivo9.write("\t")
		arquivo9.write(str(intervalo_classe1[0]))
		arquivo9.write("\t")
		arquivo9.write(str(intervalo_classe1[0]-intervalo_classe1[1]))
		arquivo9.write("\t")
		arquivo9.write(str(intervalo_classe1[0]+intervalo_classe1[1]))
		arquivo9.write("\n")

		arquivo10.write(str(e))
		arquivo10.write("\t")
		arquivo10.write(str(intervalo_classe2[0]))
		arquivo10.write("\t")
		arquivo10.write(str(intervalo_classe2[0]-intervalo_classe2[1]))
		arquivo10.write("\t")
		arquivo10.write(str(intervalo_classe2[0]+intervalo_classe2[1]))
		arquivo10.write("\n")

		arquivo11.write(str(e))
		arquivo11.write("\t")
		arquivo11.write(str(intervalo_classe3[0]))
		arquivo11.write("\t")
		arquivo11.write(str(intervalo_classe3[0]-intervalo_classe3[1]))
		arquivo11.write("\t")
		arquivo11.write(str(intervalo_classe3[0]+intervalo_classe3[1]))
		arquivo11.write("\n")

		arquivo12.write(str(e))
		arquivo12.write("\t")
		arquivo12.write(str(intervalo_bloqueio_banda[0]))
		arquivo12.write("\t")
		arquivo12.write(str(intervalo_bloqueio_banda[0]-intervalo_bloqueio_banda[1]))
		arquivo12.write("\t")
		arquivo12.write(str(intervalo_bloqueio_banda[0]+intervalo_bloqueio_banda[1]))
		arquivo12.write("\n")

	arquivo1.close()
	arquivo2.close()
	arquivo3.close()
	arquivo4.close()
	arquivo5.close()
	arquivo6.close()
	arquivo7.close()
	arquivo8.close()
	arquivo10.close()
	arquivo11.close()
	arquivo12.close()

	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
