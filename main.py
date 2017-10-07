from __future__ import print_function, division
import time
import os, shutil
from math import pi, sqrt
from random import random, randint, uniform, shuffle
from collections import namedtuple, Counter
import pickle

import numpy as np
import aabb

Genome = namedtuple('Genome', ['id', 'fight', 'grow', 'spread', 'seed_size', 'attributes', 'color'])

class Individual(object):
	def __init__(self, id, genome, x, y, radius, energy):
		self.id = id
		self.genome = genome
		self.x = x
		self.y = y
		self.start_radius = radius
		self.radius = radius
		self.next_radius = radius
		self.energy = energy
	
	def area(self):
		return pi * self.radius**2

	def distanceTo(self, other):
		return sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
	
	def combat(self, other, biases):
		""" Return who outcompetes whom. 
		"""
		a1, a2 = self.genome.attributes, other.genome.attributes
		n = len(a1)
		
		l1 = sum( n*a - np.dot(a2, biases[i]) for i, a in enumerate(a1) )
		l2 = sum( n*a - np.dot(a1, biases[i]) for i, a in enumerate(a2) )

		w1 = l1*self.area()
		w2 = l2*other.area()

		s = w1+w2

		if w1 == w2: # handle s==0 case too.
			return self if random() < .5 else other

		w1 /= s
		w2 /= s
		
		if random() < w1:
			return self
		else:
			return other
################################################################################
""" Utils
"""
def randomly_distribute(tokens, groups):
	""" Return a random list of values with sum = tokens and length = groups.
	"""
	assert type(tokens) == int and tokens >= 0
	assert type(groups) == int and groups > 0
	
	v = sorted([ randint(0, tokens) for _ in range(groups - 1) ])
	v.append(tokens)

	result = [v[0]]
	
	for i in range(1, groups):
		result.append(v[i] - v[i-1])

	return result

def create_biases(n_attributes, power):
	# Identity on diagonals
	assert power > 0 and power <= 1

	biases = np.ones((n_attributes, n_attributes))
	
	for i in range(n_attributes):
		biases[i, 1:] = np.linspace(1-power, 1+power, n_attributes-1)
		biases[i] = np.roll(biases[i], i)

	return biases

def area_to_radius(area):
	return sqrt(area/pi)

################################################################################

class Simulation(object):
	def __init__(self, width, height, n_start, n_attributes, bias_power,
				 seed_size_range, n_randseed, p_death, p_disturbance):#, p_disturb, a_disturb):
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
		self.total_attributes = 10
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
		fight, grow, spread = random(), random(), random()
		s = fight+grow+spread
		attributes = randomly_distribute(self.total_attributes,
										 self.n_attributes)
		color = (randint(0,255), randint(0,255), randint(0,255))
		
		genome = Genome(self.next_gen_id, fight/s, grow/s, spread/s, seed_size,
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
		left, right = sorted([random()*self.width, random()*self.width])
		bottom, top = sorted([random()*self.height, random()*self.height])
		
		lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)
		lower[0] = left
		lower[1] = bottom
		upper[0] = right
		upper[1] = top

		for id in self.tree.query(aabb.AABB(lower, upper)):
			self.destroyIndividual(id)

	def stepUpdateIndividuals(self, seeds):
		
		lower, upper = aabb.DoubleVector(2), aabb.DoubleVector(2)

		########################################################################
		# Update the individuals attributes, spatial map and create seeds. 
		########################################################################
		for id, ind in self.individuals.items():
			area = ind.area()
			energy = area
			
			# Area grows proportional to energy spent on it.
			new_area = area + ind.genome.grow
			ind.radius = area_to_radius(new_area)

			# Number of seeds.
			ind.energy += ind.genome.grow * energy
			n_seeds = int(ind.energy // (ind.genome.seed_size))
			ind.energy -= ind.genome.seed_size * n_seeds
			# Add to seeds list.
			seeds.append((n_seeds, ind.genome))
			
			position = aabb.DoubleVector(2)
			position[0] = ind.x
			position[1] = ind.y
			# self.tree.updateParticle(id, position, ind.radius)
			self.tree.removeParticle(id)
			self.tree.insertParticle(id, position, ind.radius)

		return seeds

	def stepSpreadSeeds(self, seeds):
		########################################################################
		# Spread seeds.
		########################################################################
		print('nseeds: ', sum(s[0] for s in seeds))
		
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
			position = aabb.DoubleVector(2)
			position[0] = ind.x
			position[1] = ind.y
			
			# self.tree.updateParticle(id, position, ind.radius)
			self.tree.removeParticle(id)
			self.tree.insertParticle(id, position, ind.radius)

		genomes = set(ind.genome.id for ind in sim.individuals.values())
		print('n_individuals', len(self.individuals))
		print('n_genomes', len(genomes))
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

def draw_sim(view, sim):
	view.start_draw()
	for ind in sim.individuals.values():
		view.draw_circle((ind.x, ind.y), ind.radius, ind.genome.color, 0)
		# view.draw_text((ind.x, ind.y), str(ind.id), font=8)

	n_genomes = len(set(ind.genome.id for ind in sim.individuals.values()))
	
	view.draw_text((10, 10), ('n_individuals: %i' % len(sim.individuals)), font=16)
	view.draw_text((10, 30), 'n_species: %i' % n_genomes)
	view.end_draw()

def prepare_dir(dir):
	if os.path.exists(dir):
		shutil.rmtree(dir)
	os.makedirs(dir)

def count_species(sim):
	c = Counter()
	for ind in sim.individuals.values():
		c[ind.genome.id] += 1
	return c

if __name__ == '__main__':
	w, h = 100, 100
	timesteps = 3000
	show = True
	save = True

	start = time.time()
	
	sim = Simulation(width=w, height=h, n_start=300, n_attributes=5, p_death=.005,
				     bias_power=.5, seed_size_range=(2, 10.), n_randseed=0,
				     p_disturbance=0.00)
	
	assert(sim.isValid())

	history = []

	if show:
		from draw import PygameDraw
		view = PygameDraw(w*5, h*5, scale=5)
		prepare_dir('./imgs')
		draw_sim(view, sim)

	for i in range(timesteps):
		print(i)
		sim.step()
		
		history.append(count_species(sim))

		if show:
			draw_sim(view, sim)
			if save:
				view.save('./imgs/%03d.jpg'%i)


	# # Print each existing genome once. 
	# genomes = set(ind.genome.id for ind in sim.individuals.values())
	# for ind in sim.individuals.values():
	# 	if ind.genome.id in genomes:
	# 		print('fight', ind.genome.fight)
	# 		print('grow', ind.genome.grow)
	# 		print('spread', ind.genome.spread)
	# 		print('seed_size', ind.genome.seed_size)
	# 		print('attributes', ind.genome.attributes)
	# 		print()
	# 		genomes.remove(ind.genome.id)
	
	print('Done in:', time.time() - start)
	pickle.dump(history, open('history.p', 'wb+'))

	if show:
		view.hold()
