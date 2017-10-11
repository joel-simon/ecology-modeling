from __future__ import print_function, division
import pickle
import numpy as np
from os.path import join as pjoin

class Reporter(object):
	"""docstring for Reporter"""
	def __init__(self):
		self.history = []
		self.genomes = dict()
		self.max_individuals = 0 # most per generation, needed for exporting as array.
	
	def addGeneration(self, sim):
		individuals = []
		self.max_individuals = max(len(sim.individuals), self.max_individuals)

		for ind in sim.individuals.values():
			individuals.append((ind.id, ind.genome.id, ind.x, ind.y, ind.area()))
			self.genomes[ind.genome.id] = ind.genome

		self.history.append(individuals)

	def save(self, directory):
		print('Saving the history to:', directory)
		
		history_arr = np.zeros((len(self.history), self.max_individuals, 5), dtype='uint32')

		for i, generation in enumerate(self.history):
			for j, individual in enumerate(generation):
				history_arr[i, j] = individual

		np.save(pjoin(directory, 'history.npy'), history_arr)

		g_out = open(pjoin(directory, 'genomes.p'), 'wb')
		pickle.dump(list(self.genomes.values()), g_out)