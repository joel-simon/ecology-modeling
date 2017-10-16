from __future__ import print_function, division
import pickle
import numpy as np
from os.path import join as pjoin
from collections import Counter

class HistoryFull(object):
	""" Store a complete representation of the run including every individual
		at each generation. Useful if sections want to generaed later and
		animated. Takes a large amount of space for longer runs.
	"""
	def __init__(self):
		self._init()

	def _init(self):
		self._genomes = dict()
		self._stepBreaks = []
		self._history_ints = []
		self._history_floats = []

	def addGeneration(self, sim):
		for ind in sim.individuals.values():
			self._history_ints.append((ind.id, ind.genome.id))
			self._history_floats.append((ind.x, ind.y, ind.area()))
			self._genomes[ind.genome.id] = ind.genome
		
		self._stepBreaks.append(len(self._history_ints))

	def save(self, filepath, config):
		print('Saving the history to:', filepath)
		
		step_breaks = np.array(self._stepBreaks, dtype='uint32')
		history_ints = np.array(self._history_ints, dtype='uint32')
		history_flaots = np.array(self._history_floats, dtype='float16')

		n_ints = 5 + config['n_attributes']
		genome_ints = np.empty((len(self._genomes), n_ints), dtype='uint32')
		genome_floats = np.empty((len(self._genomes), 4), dtype='float32')

		for i, genome in enumerate(self._genomes.values()):
			genome_ints[i, 0] = genome.id
			genome_ints[i, 1] = genome.parent
			genome_ints[i, 2:5] = genome.color
			genome_ints[i, 5:] = genome.attributes
			
			genome_floats[i, 0] = genome.fight
			genome_floats[i, 1] = genome.grow
			genome_floats[i, 2] = genome.seed
			genome_floats[i, 3] = genome.seed_size

		np.savez(filepath, step_breaks, history_ints, history_flaots, \
													 genome_ints, genome_floats)
		self._init()

class History(object):
	def __init__(self):
		self.data = []
		self.genomes = {}

	def addGeneration(self, sim):
		genome_area = Counter()
		genome_count = Counter()
		
		for ind in sim.individuals.values():
			genome_area[ind.genome.id] += ind.area()
			genome_count[ind.genome.id] += 1
			self.genomes[ind.genome.id] = ind.genome

		gen_data = [(id, n, genome_area[id]/n) for id,n in genome_count.items()]
		self.data.append(gen_data)

	def save(self, filepath, config):
		print('Saving the history to:', filepath)
		pickle.dump((self.data, self.genomes), open(filepath, 'wb'), protocol=-1)
