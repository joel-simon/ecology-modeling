from __future__ import print_function, division
import sys
import pickle

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

from os.path import join as pjoin

n = 50 # how many genomes to color individually

npzfile = np.load(sys.argv[1])

step_breaks = npzfile['arr_0']
history_ints = npzfile['arr_1']
history_floats = npzfile['arr_2']
genome_ints = npzfile['arr_3']
genome_floats = npzfile['arr_4']

print('Loaded History.')

n_gens = len(step_breaks)
n_steps = 1000
step_size = max(1, int(n_gens/n_steps))

print('step_size:', step_size)

genome_colors = {}
for i in range(genome_ints.shape[0]):
	g_id = genome_ints[i, 0]
	r, g, b = genome_ints[i, 2:5]
	genome_colors[g_id] = (float(r)/255, float(g)/255, float(b)/255)

def iterate_timesteps_individuals(g):
	start = step_breaks[g-1] if g > 0 else 0
	for i in range(start, step_breaks[g]):
		id, genome_id = history_ints[i]
		x, y, area = history_floats[i]
		yield id, genome_id, x, y, area

def n_most_common_genomes():
	max_total_area = Counter()

	for g in range(0, n_gens, step_size):

		generation_total_area = Counter()

		for id, genome_id, x, y, area in iterate_timesteps_individuals(g):
			generation_total_area[genome_id] += area

		for id, area in generation_total_area.items():
			max_total_area[id] = max(area, max_total_area.get(id, 0))

	top_genomes = zip(*max_total_area.most_common(n))[0]
	return top_genomes

# Get genomes we will plot seperately.
top_genomes = n_most_common_genomes()

# Map these from genome_id to index.
top_genome_ordering = dict(zip(top_genomes, range(len(top_genomes))))

top_genome_colors = [genome_colors[gid] for gid in top_genomes]
top_genome_colors.append((.3, .3, .3))

# Create array to store plotting.
X_area = np.zeros((n+1, n_steps))
X_count = np.zeros((n+1, n_steps))

for i in range(n_steps):
	g = i * step_size
	for id, genome_id, x, y, area in iterate_timesteps_individuals(g):
		if area == 0:
			continue
		if genome_id in top_genome_ordering:
			X_area[top_genome_ordering[genome_id], i] += area
			X_count[top_genome_ordering[genome_id], i] += 1
		else:
			X_area[-1, i] += area
			X_count[-1, i] += 1

for i in range(n_steps):
	X_area[:, i] /= X_area[:,i].sum()

print('Structured data for plotting.')

x = np.arange(n_steps) * step_size

print(x.shape)
print(X_area.shape)

f, axarr = plt.subplots(2, sharex=True, figsize=(20, 12))
axarr[0].stackplot(x, X_area, colors=top_genome_colors)
axarr[0].set_title('Species Total Area')
axarr[0].set_xlabel('Generations')
axarr[0].set_ylabel('Total Area of Species')
axarr[0].set_ylim([0, 1])

axarr[1].stackplot(x, X_count, colors=top_genome_colors)
axarr[1].set_title('Species Abundance')
axarr[1].set_xlabel('Generations')
axarr[1].set_ylabel('Abundance of Species')

plt.show()
