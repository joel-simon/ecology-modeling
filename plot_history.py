from __future__ import print_function, division
import sys
import pickle

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

from os.path import join as pjoin

n = 50
step_size = 20 # Read every 25th frame

rootdir = sys.argv[1]
history = np.load(pjoin(rootdir, 'history.npy'))


history = history[0::step_size]
genomes = pickle.load(open(pjoin(rootdir, 'genomes.p'), 'rb'))

genome_colors = {}
for genome in genomes:
	r, g, b = genome.color
	genome_colors[genome.id] = (float(r)/255, float(g)/255, float(b)/255)

print('Loaded History.')

def n_most_common_genomes():
	max_total_area = Counter()
	for k, generation in enumerate(history):
		generation_total_area = Counter()
		
		for id, genome_id, x, y, area in generation:
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
top_genome_colors.append((1.0, 1.0, 1.0))
# Create array to store.
X_area = np.zeros((n+1, len(history)))
X_count = np.zeros((n+1, len(history)))

for i, generation in enumerate(history):
	for id, genome_id, x, y, area in generation:
		if area == 0:
			continue
		if genome_id in top_genome_ordering:
			X_area[top_genome_ordering[genome_id], i] += area
			X_count[top_genome_ordering[genome_id], i] += 1
		else:
			X_area[-1, i] += area
			X_count[-1, i] += 1

for i in range(len(history)):
	X_area[:, i] /= X_area[:,i].sum()

print('Structured data for plotting.')

x = np.arange(0, len(history)*step_size, step_size)
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