from __future__ import print_function, division
import time
import os, shutil
from os.path import join as pjoin
# from random import random, uniform, shuffle
from collections import Counter
import pickle
# import argparse

from simulation import Simulation
from individual import Individual
from reporter import Reporter

################################################################################
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
	os.makedirs(dir)

################################################################################

if __name__ == '__main__':
	timesteps = 10000
	show = False
	save = False
	start = time.time()
	history = []

	# name = 'with_disturbance_long_2'
	# config = {
	# 	'width':128,
	# 	'height':128,
	# 	'n_start':300,
	# 	'n_attributes':5,
	# 	'p_death':.000,
	# 	'bias_power':.5,
	# 	'seed_size_range':(1, 5.),
	# 	'n_randseed':6,
	# 	'p_disturbance':0.125,
	# 	'disturbance_power':.25,
	# 	'seed_cost_multiplier':1,
	# }
	
	name = 'test'
	timesteps = 100
	config = {
		'width':200,
		'height':200,
		'n_start':300,
		'n_attributes':5,
		'p_death':.000,
		'bias_power':.5,
		'seed_size_range':(1, 5.),
		'n_randseed':6,
		'p_disturbance':0.0,
		'disturbance_power':.25,
		'seed_cost_multiplier':1,
	}


	# name = 'no_disturbance_large'
	# config = {
	# 	'width':200,
	# 	'height':200,
	# 	'n_start':300,
	# 	'n_attributes':5,
	# 	'p_death':.0078125,
	# 	'bias_power':.5,
	# 	'seed_size_range':(1, 5.),
	# 	'n_randseed':6,
	# 	'p_disturbance':0.0,
	# 	'disturbance_power':0.0,
	# 	'seed_cost_multiplier':1,
	# }

	assert len(name) != 0
	
	if save:
		out_dir = '/Users/joelsimon/Dropbox/projects/ecology_modelling/output/'+name+'/'
		assert not os.path.exists(out_dir)
	
	sim = Simulation(**config)
	log = Reporter()

	if save:
		prepare_dir(pjoin(out_dir, 'imgs'))
	
	if show:
		from draw import PygameDraw
		view = PygameDraw(config['width']*5, config['height']*5, scale=5)	
		draw_sim(view, sim)
	
	for i in range(timesteps):
		sim.step()
		log.addGeneration(sim)

		if i % 100  == 0:
			print('Step:', i)
			genomes = set(ind.genome.id for ind in sim.individuals.values())
			print('n_individuals:', len(sim.individuals))
			print('n_genomes:', len(genomes))
			print()

		if show:
			draw_sim(view, sim)
			if save:
				view.save(pjoin(out_dir, 'imgs/%06d.jpg'%i))
	
	print('Done in:', time.time() - start)
	# print(list(sorted(log.genomes.keys())))
	if save:
		log.save(out_dir)	
		with open(pjoin(out_dir, 'config.txt'), 'wb+') as fconfig:
			for key, value in config.items():
				fconfig.write(key+'\t'+str(value)+'\n')

