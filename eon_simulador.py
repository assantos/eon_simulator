#!/usr/bin/env python
# -*- coding: utf-8 -*-

from SimPy.Simulation import *
from random import *
from config import *
import numpy as np
import networkx as nx
import math
from itertools import islice

topology = nx.read_weighted_edgelist('topology/' + TOPOLOGY, nodetype=int)

class Desalocate(Process):
	def __init__(self):
		Process.__init__(self)
	def Run(self,count,path,spectro,holding_time):
		global topology
		yield hold, self, holding_time
		for i in range(0, (len(path)-1)):
			for slot in range(spectro[0],spectro[1]+1):
				topology[path[i]][path[i+1]]['capacity'][slot] = 0

class Simulador(Process):
	def __init__(self):
		Process.__init__(self)
		global topology
		for u, v in topology.edges_iter():
			topology[u][v]['capacity'] = [0] * SLOTS
		self.nodes = topology.nodes()
		self.random = Random()
		self.NumReqBlocked = 0 
		self.cont_req = 0
		self.NumReq_10 = 0 
		self.NumReq_20 = 0 
		self.NumReq_40 = 0 
		self.NumReq_80 = 0 
		self.NumReq_160 = 0 
		self.NumReq_200 = 0 
		self.NumReq_400 = 0 
		self.NumReq_classe1 = 0 
		self.NumReq_classe2 = 0 
		self.NumReq_classe3 = 0 
		self.NumReqBlocked_10 = 0
		self.NumReqBlocked_20 = 0
		self.NumReqBlocked_40 = 0
		self.NumReqBlocked_80 = 0
		self.NumReqBlocked_160 = 0
		self.NumReqBlocked_200 = 0
		self.NumReqBlocked_400 = 0
		self.NumReqBlocked_classe1 = 0
		self.NumReqBlocked_classe2 = 0
		self.NumReqBlocked_classe3 = 0
		self.k_paths = {}

	def Run(self, rate):
		global topology
		for i in topology.nodes():
			for j in topology.nodes():
				if i!= j:
					self.k_paths[i,j] = self.k_shortest_paths(topology, i, j, N_PATH, weight='weight')
		for count in xrange(1, NUM_OF_REQUESTS + 1):
			yield hold, self, self.random.expovariate(rate)
			class_type = np.random.choice(CLASS_TYPE, p=CLASS_WEIGHT)
			src, dst = self.random.sample(self.nodes, 2)
			bandwidth = self.random.choice(BANDWIDTH)
			holding_time = self.random.expovariate(HOLDING_TIME)
			self.conta_requisicao_banda(bandwidth)
			self.conta_requisicao_classe(class_type)
			paths = self.k_paths[src,dst]
			flag = 0
			for i in range(N_PATH):
				distance = int(self.Distance(paths[i]))
				num_slots = int(math.ceil(self.Modulation(distance, bandwidth)))
				self.check_path = self.PathIsAble(num_slots,paths[i])
				if self.check_path[0] == True:
					self.cont_req += 1
					self.FirstFit(count, self.check_path[1],self.check_path[2],paths[i])
					spectro = [self.check_path[1], self.check_path[2]]
					desalocate = Desalocate()
					activate(desalocate, desalocate.Run(count,paths[i],spectro,holding_time))
					flag = 1
					break 
			if flag == 0:
					self.NumReqBlocked +=1
					self.conta_bloqueio_requisicao_banda(bandwidth)
					self.conta_bloqueio_requisicao_classe(class_type)

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

    def FirstFit(self, u, v, num_slots, count):
        global topology
        cont_slot = []
        alocado = False
        for slot in range(0, len(topology[u][v]['capacity'])):
            if alocado == True:
                return
            if topology[u][v]['capacity'][slot] == 0:
                cont_slot.append(slot)
                if len(cont_slot) == num_slots + 1:
                    for s in cont_slot:
                        topology[u][v]['capacity'][s] = str(count)
                        if s == cont_slot[-1]:
                            topology[u][v]['capacity'][s] = 'GB'
                    alocado = True
                    break
            else:
                cont_slot = []

    def WorstFit(self, u, v, num_slots, count):
        global topology
        cont_slot = []
        best_slots = []
        slots_escolhidos = []
        cont = 0
        alocado = False
        for slot in range(0, len(topology[u][v]['capacity'])):
            if alocado == True:
                return
            
            if topology[u][v]['capacity'][slot] == 0:
                cont_slot.append(slot)
                
            else:
                if len(cont_slot) > num_slots:
                    best_slots.append(cont_slot)
                cont_slot = []

        if len(cont_slot) > num_slots:
            best_slots.append(cont_slot)
       
        for b in best_slots:
            slots_escolhidos.append(len(b))

        slots = max(slots_escolhidos)
        
        for pos, num in enumerate(slots_escolhidos):
                if num == slots:
                    index = pos
        
        for s in best_slots[index]:
            if cont == num_slots:
                topology[u][v]['capacity'][s] = 'GB'
                alocado = True
                break
            else:
                topology[u][v]['capacity'][s] = str(count)
                cont = cont + 1
               
    def BestFit(self, u, v, num_slots, count):
        global topology
        cont_slot = []
        best_slots = []
        slots_escolhidos = []
        cont = 0
        alocado = False
        for slot in range(0, len(topology[u][v]['capacity'])):
            if alocado == True:
                return

            if topology[u][v]['capacity'][slot] == 0:
                cont_slot.append(slot)
                
            else:
                if len(cont_slot) > num_slots:
                    best_slots.append(cont_slot)
                    cont_slot = []
               
        if len(cont_slot) > num_slots:
                    best_slots.append(cont_slot)

        for l in best_slots:
            slots_escolhidos.append(len(l))

        slots = Simulador.BestSlots(self, slots_escolhidos, num_slots)
        
        
        for s in best_slots[slots]:
            if cont == num_slots:
                topology[u][v]['capacity'][s] = 'GB'
                alocado = True
                break
            else:
                topology[u][v]['capacity'][s] = str(count)
                cont = cont + 1

    def BestSlots(self, slots_escolhidos, num_slots):
        result = []
        menor = 0
        if len(slots_escolhidos) == 1 or len(slots_escolhidos) == 0:
            return 0
        else:
            for l in slots_escolhidos:
                result.append(l - num_slots)
                
            menor = min(result) 

            for pos, num in enumerate(result):
                if num == menor:
                    index = pos
            return index

	# Computa numero de requesições por banda
	def conta_requisicao_banda(self, banda):
		if banda == 10:
			self.NumReq_10 +=1
		elif banda == 20:
			self.NumReq_20 +=1
		elif banda == 40: 
			self.NumReq_40 +=1
		elif banda == 80: 
			self.NumReq_80 +=1
		elif banda == 160:
			self.NumReq_160 += 1 
		elif banda == 200:
			self.NumReq_200 += 1
		else:
			self.NumReq_400 += 1

	# Computa numero de bloqueio por banda
	def conta_bloqueio_requisicao_banda(self, banda):
		if banda == 10:
			self.NumReqBlocked_10 +=1
		elif banda == 20:
			self.NumReqBlocked_20 +=1
		elif banda == 40: 
			self.NumReqBlocked_40 +=1
		elif banda == 80: 
			self.NumReqBlocked_80 +=1
		elif banda == 160:
			self.NumReqBlocked_160 +=1
		elif banda == 200:
			self.NumReqBlocked_200 +=1
		else:
			self.NumReqBlocked_400 +=1

	# Computa o número de requisições por classe
	def conta_requisicao_classe(self, classe):
		if classe == 1:
			self.NumReq_classe1 +=1
		elif classe == 2:
			self.NumReq_classe2 +=1
		else:
			self.NumReq_classe3 +=1

	# Computa número de requisições bloqueadas por classe
	def conta_bloqueio_requisicao_classe(self, classe):
		if classe == 1:
			self.NumReqBlocked_classe1 +=1
		elif classe == 2:
			self.NumReqBlocked_classe2 +=1
		else: 
			self.NumReqBlocked_classe3 +=1

