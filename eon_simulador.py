#!/usr/bin/env python
# -*- coding: utf-8 -*-

import SimPy
from SimPy import *
from SimPy.Simulation import *
from random import *
from eon_simulador import *
from config import *
import numpy as np
import networkx as nx
import math
from estatistica import *
from itertools import islice

topology = nx.read_weighted_edgelist('topology/' + TOPOLOGY, nodetype=int)

class Desalocate(Process):
	def __init__(self):
		SimPy.Simulation.Process.__init__(self)
	# Libera espectro após o holding time    
	def Run(self,count,path,spectro,holding_time):
		global topology
		yield hold, self, holding_time
		for i in range(0, (len(path)-1)):
			for slot in range(spectro[0],spectro[1]+1):
				topology[path[i]][path[i+1]]['capacity'][slot] = 0

class Simulador(Process):
	NumReqBlocked = 0
	cont_req = 0
	NumReq_10 = 0 
	NumReq_20 = 0 
	NumReq_40 = 0 
	NumReq_80 = 0
	NumReq_160 = 0
	NumReq_200 = 0
	NumReq_400 = 0
	NumReq_classe1 = 0 
	NumReq_classe2 = 0 
	NumReq_classe3 = 0 
	NumReqBlocked_10 = 0
	NumReqBlocked_20 = 0
	NumReqBlocked_40 = 0
	NumReqBlocked_80 = 0
	NumReqBlocked_160 = 0
	NumReqBlocked_200 = 0
	NumReqBlocked_400 = 0
	NumReqBlocked_classe1 = 0
	NumReqBlocked_classe2 = 0
	NumReqBlocked_classe3 = 0

	def __init__(self):
		SimPy.Simulation.Process.__init__(self)
		global topology
		for u, v in topology.edges_iter():
			topology[u][v]['capacity'] = [0] * SLOTS
		self.nodes = topology.nodes()
		self.random = Random()

	def Run(self, rate):
		global topology
		Simulador.NumReqBlocked = 0 
		Simulador.cont_req = 0
		Simulador.NumReq_10 = 0 
		Simulador.NumReq_20 = 0 
		Simulador.NumReq_40 = 0 
		Simulador.NumReq_80 = 0 
		Simulador.NumReq_160 = 0 
		Simulador.NumReq_200 = 0 
		Simulador.NumReq_400 = 0 
		Simulador.NumReq_classe1 = 0 
		Simulador.NumReq_classe2 = 0 
		Simulador.NumReq_classe3 = 0 
		Simulador.NumReqBlocked_10 = 0
		Simulador.NumReqBlocked_20 = 0
		Simulador.NumReqBlocked_40 = 0
		Simulador.NumReqBlocked_80 = 0
		Simulador.NumReqBlocked_160 = 0
		Simulador.NumReqBlocked_200 = 0
		Simulador.NumReqBlocked_400 = 0
		Simulador.NumReqBlocked_classe1 = 0
		Simulador.NumReqBlocked_classe2 = 0
		Simulador.NumReqBlocked_classe3 = 0
		k_paths = {}

		for i in topology.nodes():
			for j in topology.nodes():
				if i!= j:
					k_paths[i,j] = Simulador.k_shortest_paths(self, topology, i, j, N_PATH, weight='weight')

		for count in xrange(1, NUM_OF_REQUESTS + 1):
			yield hold, self, self.random.expovariate(rate)
			class_type = np.random.choice(CLASS_TYPE, p=CLASS_WEIGHT)
			src, dst = self.random.sample(self.nodes, 2)
			bandwidth = self.random.choice(BANDWIDTH)
			holding_time = self.random.expovariate(HOLDING_TIME)
			Simulador.conta_requisicao_banda(self, bandwidth)
			Simulador.conta_requisicao_classe(self,class_type)
			paths = k_paths[src,dst]
			flag = 0

			for i in range(N_PATH):
				distance = int(Simulador.Distance(self,paths[i]))
				num_slots = int(math.ceil(Simulador.Modulation(self, distance, bandwidth)))
				Simulador.check_path = Simulador.PathIsAble(self,num_slots,paths[i])
				if Simulador.check_path[0] == True:
					Simulador.cont_req += 1
					Simulador.FirstFit(self, count, Simulador.check_path[1],Simulador.check_path[2],paths[i])
					spectro = [Simulador.check_path[1], Simulador.check_path[2]]
					#Libera espectro após o holding time
					desalocate = Desalocate()
					SimPy.Simulation.activate(desalocate, desalocate.Run(count,paths[i],spectro,holding_time))
					flag = 1
					break 
			if flag == 0:
					Simulador.NumReqBlocked +=1
					Simulador.conta_bloqueio_requisicao_banda(self, bandwidth)
					Simulador.conta_bloqueio_requisicao_classe(self,class_type)

	# Calcula a distância do caminho de acordo com os pesos das arestas               
	def Distance(self, path):
		global topology 
		soma = 0
		for i in range(0, (len(path)-1)):
			soma += topology[path[i]][path[i+1]]['weight']
		return (soma)

	#Calcula os k-menores caminhos entre pares o-d
	def k_shortest_paths(self,G, source, target, k, weight='weight'):
		return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))

	# Calcula o formato de modulação de acordo com a distância do caminho    
	def Modulation(self, dist, demand):
		if dist <= 500:
			return (float(demand) / float(4 * SLOT_SIZE))
		elif 500 < dist <= 1000:
			return (float(demand) / float(3 * SLOT_SIZE))
		elif 1000 < dist <= 2000:
			return (float(demand) / float(2 * SLOT_SIZE)) 
		else:
			return (float(demand) / float(1 * SLOT_SIZE))

	#Realiza a alocação de espectro utilizando First-fit
	def FirstFit(self,count,i,j,path):
		global topology
		inicio = i 
		fim =j
		for i in range(0,len(path)-1):
			for slot in range(inicio,fim):
				#print slot
				topology[path[i]][path[i+1]]['capacity'][slot] = count
			topology[path[i]][path[i+1]]['capacity'][fim] = 'GB'

	# Verifica se o caminho escolhido possui espectro disponível para a demanda requisitada
	def PathIsAble(self, nslots,path):
		global topology
		cont = 0
		t = 0
		for slot in range (0,len(topology[path[0]][path[1]]['capacity'])):
			if topology[path[0]][path[1]]['capacity'][slot] == 0:
				k = 0
				for ind in range(0,len(path)-1):
					if topology[path[ind]][path[ind+1]]['capacity'][slot] == 0:
						k += 1
				if k == len(path)-1:
					cont += 1
					if cont == 1:
						i = slot
					if cont > nslots:
						j = slot
						return [True,i,j]
					if slot == len(topology[path[0]][path[1]]['capacity'])-1:
							return [False,0,0]
				else:
					cont = 0
					if slot == len(topology[path[0]][path[1]]['capacity'])-1:
						return [False,0,0]
			else:
				cont = 0
				if slot == len(topology[path[0]][path[1]]['capacity'])-1:
					return [False,0,0]

	# Computa numero de requesições por banda
	def conta_requisicao_banda(self, banda):
		if banda == 10:
			Simulador.NumReq_10 +=1
		elif banda == 20:
			Simulador.NumReq_20 +=1
		elif banda == 40: 
			Simulador.NumReq_40 +=1
		elif banda == 80: 
			Simulador.NumReq_80 +=1
		elif banda == 160:
			Simulador.NumReq_160 += 1 
		elif banda == 200:
			Simulador.NumReq_200 += 1
		else:
			Simulador.NumReq_400 += 1

	# Computa numero de bloqueio por banda
	def conta_bloqueio_requisicao_banda(self, banda):
		if banda == 10:
			Simulador.NumReqBlocked_10 +=1
		elif banda == 20:
			Simulador.NumReqBlocked_20 +=1
		elif banda == 40: 
			Simulador.NumReqBlocked_40 +=1
		elif banda == 80: 
			Simulador.NumReqBlocked_80 +=1
		elif banda == 160:
			Simulador.NumReqBlocked_160 +=1
		elif banda == 200:
			Simulador.NumReqBlocked_200 +=1
		else:
			Simulador.NumReqBlocked_400 +=1

	# Computa o número de requisições por classe
	def conta_requisicao_classe(self, classe):
		if classe == 1:
			Simulador.NumReq_classe1 +=1
		elif classe == 2:
			Simulador.NumReq_classe2 +=1
		else:
			Simulador.NumReq_classe3 +=1

	# Computa número de requisições bloqueadas por classe
	def conta_bloqueio_requisicao_classe(self, classe):
		if classe == 1:
			Simulador.NumReqBlocked_classe1 +=1
		elif classe == 2:
			Simulador.NumReqBlocked_classe2 +=1
		else: 
			Simulador.NumReqBlocked_classe3 +=1

def main(args):
	algoritmo = 'eon'
	topologia = TOPOLOGY

	arquivo1  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio'+'.dat', 'w')
	arquivo2  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_10'+'.dat', 'w')
	arquivo3  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_20'+'.dat', 'w')
	arquivo4  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_40'+'.dat', 'w')
	arquivo5  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_80'+'.dat', 'w')
	arquivo6  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_160'+'.dat', 'w')
	arquivo7  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_200'+'.dat', 'w')
	arquivo8  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_400'+'.dat', 'w')
	arquivo9  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_classe1'+'.dat', 'w')
	arquivo10  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_classe2'+'.dat', 'w')
	arquivo11  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_classe3'+'.dat', 'w')
	arquivo12  = open('plot/'+topologia+'/'+algoritmo+'/bloqueio_banda'+'.dat', 'w')

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

		for rep in xrange(10):
			rate = e / HOLDING_TIME
			seed(RANDOM_SEED[rep])
			SimPy.Simulation.initialize()
			simulador = Simulador()
			SimPy.Simulation.activate(simulador,simulador.Run(rate))
			SimPy.Simulation.simulate(until=MAX_TIME)#MAX_TIME
			print "Erlang", e, "Simulacao...", rep
			print "bloqueadas", Simulador.NumReqBlocked, "de", NUM_OF_REQUESTS
			Bloqueio.append(Simulador.NumReqBlocked / float(NUM_OF_REQUESTS))
			Bloqueio_10.append(Simulador.NumReqBlocked_10/float(Simulador.NumReq_10))
			Bloqueio_20.append(Simulador.NumReqBlocked_20/float(Simulador.NumReq_20))
			Bloqueio_40.append(Simulador.NumReqBlocked_40/float(Simulador.NumReq_40))
			Bloqueio_80.append(Simulador.NumReqBlocked_80/float(Simulador.NumReq_80))
			Bloqueio_160.append(Simulador.NumReqBlocked_80/float(Simulador.NumReq_160))
			Bloqueio_200.append(Simulador.NumReqBlocked_80/float(Simulador.NumReq_200))
			Bloqueio_400.append(Simulador.NumReqBlocked_80/float(Simulador.NumReq_400))
			Bloqueio_classe1.append(Simulador.NumReqBlocked_classe1/float(Simulador.NumReq_classe1))
			Bloqueio_classe2.append(Simulador.NumReqBlocked_classe2/float(Simulador.NumReq_classe2))
			Bloqueio_classe3.append(Simulador.NumReqBlocked_classe3/float(Simulador.NumReq_classe3))
			BD_solicitada = ((Simulador.NumReq_10)*10+(Simulador.NumReq_20)*20+(Simulador.NumReq_40)*40+(Simulador.NumReq_80)*80+(Simulador.NumReq_160)*160+(Simulador.NumReq_200)*200+(Simulador.NumReq_400)*400)
			BD_bloqueada = ((Simulador.NumReqBlocked_10)*10+(Simulador.NumReqBlocked_20)*20+(Simulador.NumReqBlocked_40)*40+(Simulador.NumReqBlocked_80)*80+(Simulador.NumReqBlocked_160)*160+(Simulador.NumReqBlocked_200)*200+(Simulador.NumReqBlocked_400)*400)
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
