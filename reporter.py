from __future__ import print_function, division
import pickle
import numpy as np
from os.path import join as pjoin

class Reporter(object):
	def __init__(self):
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
