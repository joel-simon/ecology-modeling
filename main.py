from __future__ import print_function, division
import time
import os, shutil
# from random import random, uniform, shuffle
from collections import Counter
import pickle
# import argparse

from simulation import Simulation
from individual import Individual

################################################################################
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
################################################################################

if __name__ == '__main__':
	w, h = 150, 150
	timesteps = 5000
	show = True
	save = True

	start = time.time()
	
	sim = Simulation(width=w, height=h, n_start=300, n_attributes=5, p_death=.005,
				     bias_power=.5, seed_size_range=(1, 5.), n_randseed=3,
				     p_disturbance=0.0, disturbance_power=.15,
				     seed_cost_multiplier=1)
	
	history = []

	if show:
		from draw import PygameDraw
		view = PygameDraw(w*5, h*5, scale=5)
		prepare_dir('./imgs')
		draw_sim(view, sim)

	for i in range(timesteps):
		
		sim.step()
		
		history.append(count_species(sim))

		if i % 100  == 0:
			print('Step:', i)
			genomes = set(ind.genome.id for ind in sim.individuals.values())
			print('n_individuals', len(sim.individuals))
			print('n_genomes', len(genomes))
			print()

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
