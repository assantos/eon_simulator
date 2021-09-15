#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
import numpy as np

def CalculaIntervalo(amostra):
	# calcula média e intervalo de confiança de uma amostra (t de Student) 95%. 
	media = np.mean(amostra)
	desvio = np.std(amostra, ddof=1)
	intervalo = (desvio/len(amostra))*1.833
	return [media,intervalo]
