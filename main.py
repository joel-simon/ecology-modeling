from random import random, randint, uniform
from collections import namedtuple
from math import pi, sqrt
from rtree import index
import numpy as np
from draw import PygameDraw
import os, shutil

Genome = namedtuple('Genome', ['id', 'fight', 'grow', 'spread', 'seed_size', 'attributes', 'color'])

class Individual(object):
	def __init__(self, id, genome, x, y, radius, energy):
		self.id = id
		self.genome = genome
		self.x = x
		self.y = y
		self.radius = radius
		self.energy = energy
		
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

################################################################################
""" Individuals
"""
def individual_area(s):
	return pi * s.radius**2

def individuals_combat_winner(ind1, ind2, biases):
	a1, a2 = ind1.genome.attributes, ind2.genome.attributes
	n = len(a1)
	
	l1 = sum( n*a - np.dot(a2, biases[i]) for i, a in enumerate(a1) )
	l2 = sum( n*a - np.dot(a1, biases[i]) for i, a in enumerate(a2) )

	w1 = l1*individual_area(ind1)
	w2 = l2*individual_area(ind2)

	s = w1+w2

	if w1 == w2: # handle s==0 case too.
		return ind1 if random() < .5 else ind2

	w1 /= s
	w2 /= s
	
	if random() < w1:
		return ind1
	else:
		return ind2

def individuals_overlap(a, b):
	d = sqrt((a.x - b.x)**2 + (a.y - b.y)**2)
	return d <= (a.radius + b.radius)

################################################################################

class Simulation(object):
	def __init__(self, width, height, n_start, n_attributes, bias_power,
				 seed_size_range, n_randseed, p_death, p_disturbance):#, p_disturb, a_disturb):
		self.width = width
		self.height = height
		self.n_start = n_start
		self.n_attributes = n_attributes
		self.bias_power = bias_power
		self.seed_size_range = seed_size_range
		self.n_randseed = n_randseed
		self.p_death = p_death
		self.p_disturbance = p_disturbance
		
		
		self.next_ind_id = 0
		self.next_gen_id = 0
		self.individuals = dict()
		self.biases = create_biases(self.n_attributes, self.bias_power)

		self.total_attributes = 10

		for _ in range(n_start):
			g = self.new_random_genome()
			x = random() * width
			y = random() * height
			self.new_individual(g, x, y, g.seed_size)

	def new_random_genome(self):
		seed_size = uniform(*self.seed_size_range)
		fight, grow, spread = random(), random(), random()
		s = fight+grow+spread
		attributes = randomly_distribute(self.total_attributes, self.n_attributes)
		color = (randint(0,255), randint(0,255), randint(0,255))
		
		genome = Genome(self.next_gen_id, fight/s, grow/s, spread/s, seed_size,
			 												  attributes, color)
		self.next_gen_id += 1
		return genome

	def new_individual(self, g, x, y, seed_size):
		energy = pi * seed_size * seed_size
		ind = Individual(self.next_ind_id, g, x, y, seed_size, energy)
		self.next_ind_id += 1
		self.individuals[ind.id] = ind
		return ind

	def disturb(self):
		left, right = sorted([random()*self.width, random()*self.width])
		bottom, top = sorted([random()*self.height, random()*self.height])
		
		for id in self.tree.intersection((left, bottom, right, top )):
			del self.individuals[id]

	def death(self, ind):
		if random() < self.p_death:
			return True

		coords = (ind.x-ind.radius, ind.y-ind.radius,
				  ind.x+ind.radius, ind.y+ind.radius)
		for id2 in self.tree.intersection(coords):
			if id2 not in self.individuals:
				continue

			ind2 = self.individuals[id2]

			if id2 == ind.id:
				continue

			if not individuals_overlap(ind, ind2):
				continue

			if individuals_combat_winner(ind, ind2, self.biases) == ind2:
				return True

		return False

	def step(self):
		self.tree = index.Index()
		seeds = [(1, self.new_random_genome()) for _ in range(self.n_randseed)]

		for ind in self.individuals.values():
			energy = individual_area(ind)
			area = individual_area(ind)
			ind.radius = sqrt((area+ind.genome.grow)/pi)
			ind.energy += ind.genome.grow * energy
			n_seeds = int(ind.energy // (ind.genome.seed_size * 2))
			ind.energy -= ind.genome.seed_size * n_seeds
			seeds.append((n_seeds, ind.genome))
		
		for ind in self.individuals.values():
			coords = (ind.x-ind.radius, ind.y-ind.radius,
					  ind.x+ind.radius, ind.y+ind.radius)
			self.tree.insert(ind.id, coords)

		if random() < self.p_disturbance:
			print('Disturbed.')
			self.disturb()
		
		for id in list(self.individuals.keys()):
			if self.death(self.individuals[id]):
				del self.individuals[id]

		for n, genome in seeds:
			for i in range(n):
				x, y = random() * self.width, random() * self.height
				r = genome.seed_size

				coords = (x-r, y-r, x+r,  y+r)
				if not any(self.tree.intersection(coords)):
					ind = self.new_individual(genome, x, y, r)
					self.tree.insert(ind.id, coords)

					break

def draw_sim(view, sim):
	view.start_draw()
	for ind in sim.individuals.values():
		view.draw_circle((ind.x, ind.y), ind.radius, ind.genome.color, 0)
	n_genomes = len(set(ind.genome.id for ind in sim.individuals.values()))
	view.draw_text((10, 10), ('n_individuals: %i' % len(sim.individuals)), font=16)
	view.draw_text((10, 30), 'n_species: %i' % n_genomes)
	view.end_draw()

def prepare_dir(dir):
	if os.path.exists(dir):
		shutil.rmtree(dir)
	   #  for the_file in os.listdir(dir):
		  #   file_path = os.path.join(dir, the_file)
		  #   try:
		  #       if os.path.isfile(file_path):
		  #           os.unlink(file_path)
	# else:
	os.makedirs(dir)
	
if __name__ == '__main__':
	w, h = 100, 100
	timesteps = 300

	sim = Simulation(width=w, height=h, n_start=100, n_attributes=5,p_death=.03,
				     bias_power=.5, seed_size_range=(1, 4), n_randseed=3,
				     p_disturbance=0.5)

	view = PygameDraw(w*5, h*5, scale=5)
	
	prepare_dir('./imgs')

	draw_sim(view, sim)

	for i in range(timesteps):
		sim.step()
		draw_sim(view, sim)
		print(i)
		view.save('./imgs/%03d.jpg'%i)

	# Print each existing genome once. 
	genomes = set(ind.genome.id for ind in sim.individuals.values())
	for ind in sim.individuals.values():
		if ind.genome.id in genomes:
			print('fight', ind.genome.fight)
			print('grow', ind.genome.grow)
			print('spread', ind.genome.spread)
			print('seed_size', ind.genome.seed_size)
			print('attributes', ind.genome.attributes)
			print()
			genomes.remove(ind.genome.id)

	view.hold()
