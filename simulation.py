from __future__ import print_function, division
from math import pi, sqrt
from random import random, randint, uniform, shuffle
from collections import namedtuple

import aabb

from individual import Individual
from utils import randomly_distribute, create_biases, area_to_radius

Genome = namedtuple('Genome', ['id', 'fight', 'grow', 'seed', 'seed_size', 'attributes', 'color'])

class Simulation(object):
	def __init__(self, width, height, n_start, n_attributes, bias_power,
				 seed_size_range, n_randseed, p_death, p_disturbance,
				 disturbance_power, seed_cost_multiplier):
		########################################################################
		self.width = width
		self.height = height
		self.n_start = n_start
		self.n_attributes = n_attributes
		self.bias_power = bias_power
		self.seed_size_range = seed_size_range # Starting seed size (IN AREA)
		self.n_randseed = n_randseed
		self.p_death = p_death
		self.p_disturbance = p_disturbance
		self.disturbance_power = disturbance_power
		self.total_attributes = 10
		self.seed_cost_multiplier = seed_cost_multiplier
		########################################################################
		self.next_ind_id = 0
		self.next_gen_id = 0
		########################################################################		
		self.individuals = dict()
		self.biases = create_biases(self.n_attributes, self.bias_power)
		########################################################################
		self.tree = aabb.Tree(2)

		for _ in range(n_start):
			g = self.randomGenome()
			x = random() * width
			y = random() * height
			self.createIndividual(g, x, y, g.seed_size)

	def randomGenome(self):
		seed_size = uniform(*self.seed_size_range)
		fight, grow, seed = random(), random(), random()
		s = fight+grow+seed
		attributes = randomly_distribute(self.total_attributes,
										 self.n_attributes)
		color = (randint(0,255), randint(0,255), randint(0,255))
		
		genome = Genome(self.next_gen_id, fight/s, grow/s, seed/s, seed_size,
			 												  attributes, color)
		self.next_gen_id += 1
		return genome

	def isEmptySpace(self, x, y, r):
		if self.tree.getNodeCount() == 0:
			return True
		lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
		lower[0] = x - r
		lower[1] = y - r
		upper[0] = x + r
		upper[1] = y + r
		AABB = aabb.AABB(lower, upper)
		return len(self.tree.query(AABB)) == 0

	def createIndividual(self, g, x, y, seed_size):
		""" Returns the individuals id.
		"""
		radius = area_to_radius(seed_size)

		if not self.isEmptySpace(x, y, radius):
			return None

		energy = pi * radius * radius
		ind = Individual(self.next_ind_id, g, x, y, radius, energy)
		
		self.next_ind_id += 1
		self.individuals[ind.id] = ind

		# Add to spatial tree.
		position = aabb.DoubleVector(2)
		position[0] = x
		position[1] = y
		self.tree.insertParticle(ind.id, position, radius)

		return ind

	def destroyIndividual(self, id):
		del self.individuals[id]
		self.tree.removeParticle(id)

	def disturbRectangle(self):
		lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
		lower[0] = random()*(self.width * (1 - self.disturbance_power))
		lower[1] = random()*(self.height * (1 - self.disturbance_power))
		upper[0] = lower[0] + self.width*self.disturbance_power
		upper[1] = lower[1] + self.height*self.disturbance_power

		for id in self.tree.query(aabb.AABB(lower, upper)):
			self.destroyIndividual(id)

	def stepUpdateIndividuals(self, seeds):
		""" Update the individuals attributes, spatial map and create seeds. 
			We change the seed list in place.
			'seeds' is a list of tuples [(n_seeds, genome), ...]
		"""
		lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
		for id, ind in self.individuals.items():
			ind_area = ind.area()
			new_energy = ind_area
			
			grow_energy = new_energy * ind.genome.grow
			seed_energy = new_energy * ind.genome.seed

			# growth is based on energy spent on it and 3.4 powe rule.
			# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC33381/
			new_growth = grow_energy**.75
			ind.radius = area_to_radius(ind_area + new_growth)

			# Number of seeds.
			seed_cost = ind.genome.seed_size * self.seed_cost_multiplier
			num_seeds = int(ind.energy // seed_cost)
			seeds.append((num_seeds, ind.genome))
			
			# Update spatial map
			self.updateIndividualSpatialTree(ind)

		return seeds

	def updateIndividualSpatialTree(self, ind):
		position = aabb.DoubleVector(2)
		position[0] = ind.x
		position[1] = ind.y

		# self.tree.updateParticle(id, position, ind.radius)
		self.tree.removeParticle(ind.id)
		self.tree.insertParticle(ind.id, position, ind.radius)

	def stepSpreadSeeds(self, seeds):
		########################################################################
		# Spread seeds.
		########################################################################
		# print('nseeds: ', sum(s[0] for s in seeds))
		
		# Iterate through seeds in random order.
		shuffle(seeds)
		for n, genome in seeds:
			for _ in range(n):
				x, y = random() * self.width, random() * self.height
				self.createIndividual(genome, x, y, genome.seed_size)

	def step(self):
		lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
		seeds = [(1, self.randomGenome()) for _ in range(self.n_randseed)]
		
		self.stepUpdateIndividuals(seeds)
		self.stepSpreadSeeds(seeds)

		########################################################################
		# Killing time.
		########################################################################
		if random() < self.p_disturbance:
			print('Disturbance.')
			self.disturbRectangle()

		for ind in self.individuals.values():
			ind.next_radius = ind.radius

		# Create copy of list so we can edit while we iterate
		for id, ind in list(self.individuals.items()):
			
			if id not in self.individuals:
				continue
			
			if random() < self.p_death: # Chance of random death.
				self.destroyIndividual(id)
				continue

			for id_other in self.tree.query(id):
				if id_other == id:
					continue

				ind_other = self.individuals[id_other]
				dist = ind.distanceTo(ind_other)
				
				# If overlapping.
				if dist > (ind.radius + ind_other.radius):
					continue
				
				winner = ind.combat(ind_other, self.biases)
				loser = ind if winner is ind_other else ind_other

				# If the winner covers the center of loser, then loser dies.
				if dist < winner.radius:
					self.destroyIndividual(loser.id)
				else:
					# The loser shrinks.
					loser.next_radius = min(loser.next_radius, (dist - winner.radius) * .95)
					
					assert loser.next_radius < loser.radius, (loser.next_radius,loser.radius)

					if loser.next_radius <= loser.start_radius:
						self.destroyIndividual(loser.id)	

				# Stop checking others if this individual died
				if loser is ind:
					break

		for id, ind in self.individuals.items():
			ind.radius = ind.next_radius
			self.updateIndividualSpatialTree(ind)

		# assert(self.isValid())

	def isValid(self):
		for id1, ind1 in self.individuals.items():
			for id2, ind2 in self.individuals.items():
				if id1 == id2:
					continue
				d = ind1.distanceTo(ind2)
				if d < ind1.radius + ind2.radius:
					print(d, ind1.radius+ind2.radius,(ind1.x, ind1.y, ind1.radius), (ind2.x, ind2.y, ind2.radius))
					print(id1, id2)
					return False
		return True